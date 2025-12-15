import psycopg2
from collections import Counter

DB_CONFIG = {
    "dbname": "streaming_service",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def query_1_sql(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select region
            from driver
            group by region
            having count(*) > 15
            """
        )
        return [row[0] for row in cur.fetchall()]


def query_1_app(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT region FROM driver;")
        regions = [row[0] for row in cur.fetchall()]

    counter = Counter(regions)
    return [region for region, cnt in counter.items() if cnt > 15]


def query_2_sql(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            with arrivals as (
                select fio,
                    date_route,
                    time_route,
                    rank() over (order by date_route, time_route) as rn
                from route r
                join driver d 
                on d.id = r.driver_id 
                where type = 1
            )

            select fio, date_route, time_route
            from arrivals
            where rn = 1
            """
        )
        return [row[0] for row in cur.fetchall()]


def query_2_app(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT fio, date_route, time_route from route r join driver d on d.id = r.driver_id where type = 1;
        """)
        arrivals = [row for row in cur.fetchall()]

    arrivals.sort(key=lambda x: (x[1], x[2]))
    first_arrival = arrivals[0]
    result = [arrival[0] for arrival in arrivals if arrival[1] == first_arrival[1] and arrival[2] == first_arrival[2]]
    return result


def query_3_sql(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            with route_with_datetime as (
                select 
                    driver_id,
                    date_route::date + time_route::time as datetime_route,
                    type
                from route
            )
            , route_cur_date_and_prev_date as (
                select 
                    driver_id,
                    datetime_route,
                    lag(datetime_route) over (partition by driver_id order by datetime_route) as prev_d,
                    type
                from route_with_datetime
            )
            , filtered_arrivals_route as (
                select 
                    driver_id,
                    datetime_route,
                    prev_d,
                    datetime_route - interval '100 day' as day_100
                from route_cur_date_and_prev_date
                where type = 0 and prev_d is not null
            )

            select fio
            from filtered_arrivals_route
            join driver d on d.id = driver_id 
            where day_100 > prev_d
            """
        )
        return [row[0] for row in cur.fetchall()]


def query_3_app(conn, days=100):
    with conn.cursor() as cur:
        cur.execute(
            """
            select 
                driver_id, 
                date_route::date + time_route::time as datetime_route,
                type
            from route;            
            """
        )
        rows_route = cur.fetchall()

    with conn.cursor() as cur:
        cur.execute(
            """
            select id, fio
            from driver;
            """
        )
        rows_driver = cur.fetchall()

    last_date_by_driver = {}
    result = set()

    for driver_id, datetime_route, type in rows_route:
        prev = last_date_by_driver.get(driver_id)
        if prev is not None and (datetime_route - prev).days > days and type == 0:
            result.add(driver_id)
        last_date_by_driver[driver_id] = datetime_route

    return [row[1] for row in rows_driver if row[0] in result]


def process_result(result):
    return ", ".join(result)


def main():
    conn = get_connection()

    print("Регионы (SQL):", process_result(query_1_sql(conn)))
    print("Регионы (Python):", process_result(query_1_app(conn)))
    print("Первый вернувшийся (SQL):", process_result(query_2_sql(conn)))
    print("Первый вернувшийся (Python):", process_result(query_2_app(conn)))
    print("Водители с перерывом > 100 дней (SQL):", process_result(query_3_sql(conn)))
    print("Водители с перерывом > 100 дней (Python):", process_result(query_3_app(conn)))
    
    conn.close()


if __name__ == "__main__":
    main()
