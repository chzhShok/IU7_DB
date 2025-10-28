import psycopg2
import pandas as pd


class StreamingServiceDB:
    def __init__(self):
        try:
            self.__conn = psycopg2.connect(
                host="localhost",
                database="streaming_service",
                user="postgres",
                password="postgres",
                port="5432",
            )
            self.__conn.autocommit = True
            self.__cur = self.__conn.cursor()
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")

    def __del__(self):
        if self.__conn:
            self.__cur.close()
            self.__conn.close()
            print("PostgreSQL connection closed\n")

    def __sql_executor(self, sql_query):
        try:
            self.__cur.execute(sql_query)
        except Exception as e:
            print(f"Error executing query: {e}")
            return

        return sql_query

    def __to_pandas_df(self, rows):
        columns = [desc[0] for desc in self.__cur.description]

        df = pd.DataFrame(rows, columns=columns)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

        return df

    # 1. Выполнить скалярный запрос
    def avg_movies_release_year(self):
        sql_query = """
        select 
            avg(release_year) as avg_release_year
        from cinema.movies
        """

        if self.__sql_executor(sql_query):
            row = self.__cur.fetchone()
            return row[0]

    # 2. Выполнить запрос с несколькими соединениями
    def users_statistic(self):
        sql_query = """
        select distinct
            u.user_id,
            u.full_name as user,
            u.email as email,
            u.subscription_type as subscription_type,
            u.registration_date as registration_date,
            count(vh.view_id) over(partition by u.user_id) as total_views,
            avg(vh.viewed_percentage) over(partition by u.user_id) as avg_percentage_views,
            count(d.device_id) over(partition by u.user_id) as device_count,
            count(pm.payment_method_id) over(partition by u.user_id) as payment_method_count
        from cinema.users u
        left join cinema.viewing_history vh on u.user_id = vh.user_id
        left join cinema.devices d on u.user_id = d.user_id and d.is_active = true
        left join cinema.payment_methods pm on u.user_id = pm.user_id
        order by u.user_id
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)

            return df

    # 3. Выполнить запрос с CTE и оконными функциями
    def movies_rating(self):
        sql_query = """
        with movie_ratings as (
            select
                m.movie_id,
                m.title,
                m.director,
                m.release_year,
                m.genres,
                m.imdb_rating,
                count(vh.view_id) as total_views,
                avg(vh.viewed_percentage) as avg_completion_rate
            from cinema.movies m
            left join cinema.viewing_history vh on m.movie_id = vh.movie_id
            group by m.movie_id, m.title, m.director, m.release_year, m.genres, m.imdb_rating
        ),
        genre_analysis as (
            select
                genre,
                count(*) as movie_count,
                round(avg(imdb_rating), 2) as avg_imdb_rating,
                round(avg(avg_completion_rate), 2) as avg_completion_rate,
                sum(total_views) as total_views
            from movie_ratings,
            lateral unnest(string_to_array(genres, ',')) as genre
            group by genre
        )
        select * from genre_analysis
        where genre is not null and genre != ''
        order by total_views desc
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)

            return df

    # 4. Выполнить запрос к метаданным
    def table_columns_information(self):
        sql_query = """
        select 
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        from information_schema.columns 
        where table_schema = 'cinema'
        order by table_name, ordinal_position;
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)

            return df

    # 5. Вызвать скалярную функцию
    def director_avg_rating(self):
        sql_query = """
        create or replace function get_director_avg_rating(director_name text)
        returns decimal as $$
        declare
            avg_rating decimal;
        begin
            select avg(imdb_rating) into avg_rating
            from cinema.movies 
            where director = director_name;
            
            return coalesce(avg_rating, 0);
        end;
        $$ language plpgsql;
        
        select 
            director,
            get_director_avg_rating(director) as avg_rating
        from cinema.movies 
        group by director
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)

            return df

    # 6. Вызвать многооператорную или табличную функцию
    def users_by_subscription(self, subscription_type):
        sql_query = f"""
        create or replace function get_users_by_subscription(sub_type text)
        returns table (
            user_id int,
            email text,
            full_name text,
            registration_date date
        ) as $$
        begin
            return query
            select u.user_id, u.email, u.full_name, u.registration_date
            from cinema.users u
            where u.subscription_type = sub_type
            order by u.registration_date desc;
        end;
        $$ language plpgsql;
        
        select * from get_users_by_subscription('{subscription_type}')
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)
            return df

    # 7. Вызвать хранимую процедуру
    def update_user_subscription(self, user_id, new_subscription_type):
        sql_query = f"""
        create or replace procedure update_user_subscription(
            p_user_id int,
            p_new_subscription text
        ) as $$
        begin
            if p_new_subscription not in ('basic', 'standard', 'premium') then
                raise exception 'invalid subscription type: %', p_new_subscription;
            end if;
            
            update cinema.users 
            set subscription_type = p_new_subscription
            where user_id = p_user_id;
            
            raise notice 'subscription updated for user % to %', p_user_id, p_new_subscription;            
        end;
        $$ language plpgsql;
        
        call update_user_subscription({1}, '{new_subscription_type}');
        
        select user_id, subscription_type
        from cinema.users
        where user_id = {user_id};
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)
            return df

    # 8. Вызвать системную функцию или процедуру
    def database_size(self):
        sql_query = """
        select pg_size_pretty(pg_database_size('streaming_service')) as db_size
        """

        if self.__sql_executor(sql_query):
            rows = self.__cur.fetchall()
            df = self.__to_pandas_df(rows)
            return df

    # 9. Создать таблицу в базе данных
    def create_review_table(self):
        sql_query = """
        drop table if exists cinema.user_reviews;
        
        create table cinema.user_reviews (
            review_id serial primary key,
            user_id integer not null,
            movie_id integer not null,
            rating integer not null check (rating between 1 and 10),
            review_text text,
            created_at timestamp default current_timestamp,
                        
            constraint fk_user_review_user foreign key (user_id) references cinema.users(user_id) on delete cascade,
            constraint fk_user_review_movie foreign key (movie_id) references cinema.movies(movie_id) on delete cascade,
            constraint unique_user_movie_review unique (user_id, movie_id)
        );
        """

        if self.__sql_executor(sql_query):
            print("Review table created")

    # 10. Выполнить вставку данных в созданную таблицу с использованием инструкции INSERT или COPY
    def insert_user_review(self):
        sql_query = """
        insert into cinema.user_reviews (user_id, movie_id, rating, review_text)
        select 
            u.user_id,
            m.movie_id,
            (random() * 9 + 1)::integer as rating,
            case 
                when random() > 0.3 then 
                    case (random() * 5)::integer
                        when 0 then 'Отличный фильм!'
                        when 1 then 'Очень понравилось'
                        when 2 then 'Неплохо, но есть недостатки'
                        when 3 then 'Разочарован'
                        when 4 then 'Шедевр!'
                    end
                else null
            end as review_text
        from 
            cinema.users u
        cross join 
            cinema.movies m
        where 
            random() < 0.1
        limit 50;
        """

        if self.__sql_executor(sql_query):
            print("Data inserted\n")

            sql_query = "select * from cinema.user_reviews;"
            if self.__sql_executor(sql_query):
                rows = self.__cur.fetchall()
                df = self.__to_pandas_df(rows)
                return df

    # 11. DROP DATABASE
    def drop_database(self):
        if self.__conn:
            self.__cur.close()
            self.__conn.close()
            print("Connection to streaming_service closed")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="postgres",
                port="5432",
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            cur.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'streaming_service'
                AND pid <> pg_backend_pid();
            """)
            
            cur.execute("DROP DATABASE IF EXISTS streaming_service;")
            print("Database streaming_service dropped successfully")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error dropping database: {e}")
