import psycopg2
import redis
import json
import time
import csv
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta

output_dir = "plots"
csv_dir = "csv"
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
dpi = 100
figsize = (1920 / dpi, 1080 / dpi)

QUERY = """
    SELECT 
        m.movie_id,
        m.title,
        COUNT(vh.view_id) AS total_views,
        AVG(vh.viewed_percentage) AS avg_completion
    FROM cinema.viewing_history vh
    JOIN cinema.movies m ON vh.movie_id = m.movie_id
    GROUP BY m.movie_id, m.title
    ORDER BY total_views DESC
    LIMIT 10;
"""

KEY = "query:top_movies_stats"
SLEEP_TIME = 5
ADD_TIME = 10
DELETE_TIME = 10
UPDATE_TIME = 10

def get_cursor_to_db():
    connection = psycopg2.connect(
        dbname="streaming_service",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )
    if connection is None:
        return None
    cursor = connection.cursor()
    return cursor

def get_redis():
    return redis.Redis(host='localhost', port=6379, decode_responses=True)

def query_postgres(cursor, query):
    t_start = time.perf_counter()
    cursor.execute(query)
    rows = cursor.fetchall()
    t_end = time.perf_counter()
    return rows, t_end - t_start

def query_redis(redis_client, cursor, key, query):
    t_start = time.perf_counter()
    val = redis_client.get(key)
    if val is not None:
        rows = json.loads(val)
        source = "redis"
        delta_time = time.perf_counter() - t_start
        return rows, delta_time, source

    rows, _ = query_postgres(cursor, query)
    redis_client.set(key, json.dumps(rows, default=str))  
    delta_time = time.perf_counter() - t_start
    return rows, delta_time, "db->set"

def plot_pg_redis(csv_path: str, title: str, outfile_stem: str):
    df = pd.read_csv(csv_path)
    
    df["iteration"] = df["iteration"].astype(int)
    df["pg_time"] = df["pg_time"].astype(float)
    df["redis_time"] = df["redis_time"].astype(float)
    
    plt.figure(figsize=figsize, dpi=dpi)

    plt.plot(
        df["iteration"], df["pg_time"],
        color="orange", linestyle="-", linewidth=2,
        marker="o", markersize=6, label="PostgreSQL", zorder=5
    )
    plt.plot(
        df["iteration"], df["redis_time"],
        color="royalblue", linestyle="-", linewidth=2,
        marker="^", markersize=6, label="Redis (cache)", zorder=6
    )

    if "source" in df.columns:
        mask_set = df["source"].astype(str).str.lower().eq("db->set")
        if mask_set.any():
            plt.scatter(
                df.loc[mask_set, "iteration"],
                df.loc[mask_set, "redis_time"],
                marker="x", s=70, color="crimson", linewidths=2,
                label="Пересчёт кэша", zorder=10
            )

    xticks = np.arange(df["iteration"].min(), df["iteration"].max() + 1)
    plt.xticks(xticks[::max(1, len(xticks)//20)])
    plt.grid(True, which='major', axis='both', linestyle='-', alpha=0.3, linewidth=0.5)
    plt.grid(True, which='minor', axis='both', linestyle=':', alpha=0.2, linewidth=0.5)
    plt.minorticks_on()

    plt.title(title, fontsize=16, pad=20)
    plt.xlabel("Номер итерации", fontsize=14)
    plt.ylabel("Время запроса (с)", fontsize=14)
    plt.legend(fontsize=10, loc='best')
    plt.tight_layout()

    svg_path = os.path.join(output_dir, f"{outfile_stem}.svg")
    plt.savefig(svg_path, bbox_inches='tight')
    plt.close()
    print(f"График сохранился в: {svg_path}\n")

def task_03_01(cursor, redis_client):
    print("Тест 3.1: Без изменения данных в БД")
    csv_path = "csv/task_03_01.csv"
    
    with open(csv_path, "w", newline="") as file:
        w = csv.writer(file)    
        w.writerow(["iteration", "pg_time", "redis_time", "source"])
        
        for i in range(20):
            rows_pg, t_pg = query_postgres(cursor, QUERY)
            
            rows_redis, t_redis, source = query_redis(redis_client, cursor, KEY, QUERY)
            
            w.writerow([i, round(t_pg, 6), round(t_redis, 6), source])
            print(f"iter {i}: PG={t_pg:.5f}s, Redis={t_redis:.5f}s, source={source}")
            
            time.sleep(SLEEP_TIME)
    
    plot_pg_redis(csv_path, "Сравнительный анализ времени выполнения запросов PostgreSQL и Redis\nБез изменения данных в БД", "task_03_01")

def task_03_02(cursor, redis_client):
    print("Тест 3.2: При добавлении новых строк каждые 10 секунд")
    csv_path = "csv/task_03_02.csv"
    
    cursor.execute("SELECT user_id FROM cinema.users LIMIT 3")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT movie_id FROM cinema.movies LIMIT 3")
    movie_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT device_id FROM cinema.devices LIMIT 3")
    device_ids = [row[0] for row in cursor.fetchall()]
    
    start_time = time.time()
    next_add = start_time + ADD_TIME
    
    with open(csv_path, "w", newline="") as file:
        w = csv.writer(file)
        w.writerow(["iteration", "pg_time", "redis_time", "source"])
        
        for i in range(20):
            rows_pg, t_pg = query_postgres(cursor, QUERY)
            
            rows_redis, t_redis, source = query_redis(redis_client, cursor, KEY, QUERY)
            
            w.writerow([i, round(t_pg, 6), round(t_redis, 6), source])
            print(f"iter {i}: PG={t_pg:.5f}s, Redis={t_redis:.5f}s, source={source}")
            
            current_time = time.time()
            if current_time >= next_add:
                user_id = random.choice(user_ids)
                movie_id = random.choice(movie_ids)
                device_id = random.choice(device_ids)
                
                start_time_view = datetime.now() - timedelta(hours=random.randint(10, 24))
                end_time_view = start_time_view + timedelta(minutes=random.randint(10, 120))
                viewed_percentage = random.randint(10, 100)
                
                cursor.execute(
                    "INSERT INTO cinema.viewing_history (user_id, movie_id, device_id, start_time, end_time, viewed_percentage) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, movie_id, device_id, start_time_view, end_time_view, viewed_percentage)
                )
                cursor.connection.commit()
                
                redis_client.delete(KEY)
                print(f"Добавлена новая запись просмотра (user={user_id}, movie={movie_id}, devica={device_id})")
                
                next_add = current_time + ADD_TIME
            
            time.sleep(SLEEP_TIME)
    
    plot_pg_redis(csv_path, "Сравнительный анализ времени выполнения запросов PostgreSQL и Redis\nПри добавлении новых строк каждые 10 секунд", "task_03_02")

def task_03_03(cursor, redis_client):
    print("Тест 3.3: При удалении строк каждые 10 секунд")
    csv_path = "csv/task_03_03.csv"
    
    start_time = time.time()
    next_delete = start_time + DELETE_TIME
    
    with open(csv_path, "w", newline="") as file:
        w = csv.writer(file)
        w.writerow(["iteration", "pg_time", "redis_time", "source"])
        
        for i in range(20):
            rows_pg, t_pg = query_postgres(cursor, QUERY)
            
            rows_redis, t_redis, source = query_redis(redis_client, cursor, KEY, QUERY)
            
            w.writerow([i, round(t_pg, 6), round(t_redis, 6), source])
            print(f"iter {i}: PG={t_pg:.5f}s, Redis={t_redis:.5f}s, source={source}")
            
            current_time = time.time()
            if current_time >= next_delete:
                cursor.execute("SELECT view_id FROM cinema.viewing_history ORDER BY RANDOM() LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    view_id = result[0]
                    cursor.execute("DELETE FROM cinema.viewing_history WHERE view_id = %s", (view_id,))
                    cursor.connection.commit()

                    redis_client.delete(KEY)
                    print(f"Удалена запись просмотра (view_id={view_id})")
                
                next_delete = current_time + DELETE_TIME
            
            time.sleep(SLEEP_TIME)
    
    plot_pg_redis(csv_path, "Сравнительный анализ времени выполнения запросов PostgreSQL и Redis\nПри удалении строк каждые 10 секунд", "task_03_03")

def task_03_04(cursor, redis_client):
    print("Тест 3.4: При изменении строк каждые 10 секунд")
    csv_path = "csv/task_03_04.csv"
    
    start_time = time.time()
    next_update = start_time + UPDATE_TIME
    
    with open(csv_path, "w", newline="") as file:
        w = csv.writer(file)
        w.writerow(["iteration", "pg_time", "redis_time", "source"])
        
        for i in range(20):
            rows_pg, t_pg = query_postgres(cursor, QUERY)
            
            rows_redis, t_redis, source = query_redis(redis_client, cursor, KEY, QUERY)
            
            w.writerow([i, round(t_pg, 6), round(t_redis, 6), source])
            print(f"iter {i}: PG={t_pg:.5f}s, Redis={t_redis:.5f}s, source={source}")
            
            current_time = time.time()
            if current_time >= next_update:
                cursor.execute("SELECT view_id FROM cinema.viewing_history ORDER BY RANDOM() LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    view_id = result[0]
                    new_percentage = random.randint(10, 100)
                    
                    cursor.execute(
                        "UPDATE cinema.viewing_history SET viewed_percentage = %s WHERE view_id = %s",
                        (new_percentage, view_id)
                    )
                    cursor.connection.commit()
                    
                    redis_client.delete(KEY)
                    print(f"Обновлена запись просмотра (view_id={view_id}, новый процент={new_percentage}%)")
                
                next_update = current_time + UPDATE_TIME
            
            time.sleep(SLEEP_TIME)
    
    plot_pg_redis(csv_path, "Сравнительный анализ времени выполнения запросов PostgreSQL и Redis\nПри изменении строк каждые 10 секунд", "task_03_04")

def generate_summary_report():
    scenarios = [
        ("csv/task_03_01.csv", "Без изменений"),
        ("csv/task_03_02.csv", "С добавлением"),
        ("csv/task_03_03.csv", "С удалением"), 
        ("csv/task_03_04.csv", "С обновлением")
    ]
    
    print("\n" + "="*80)
    print("СВОДНЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ")
    print("="*80)
    print(f"{'Сценарий':<15} {'Pg Avg':<9} {'Redis Avg':<11} {'Ускорение':<12}")
    print("-"*80)
    
    for csv_file, scenario_name in scenarios:
        try:
            df = pd.read_csv(csv_file)
            avg_pg = df['pg_time'].mean()
            avg_redis = df['redis_time'].mean()
            speedup = avg_pg / avg_redis if avg_redis > 0 else 0
            
            print(f"{scenario_name:<15} {avg_pg:.4f}s   {avg_redis:.4f}s     {speedup:.2f}x")
        except FileNotFoundError:
            print(f"{scenario_name:<15} {'N/A':<10} {'N/A':<10} {'N/A':<12}")
    
    print("="*80)

if __name__ == "__main__":
    cursor = get_cursor_to_db()
    redis_client = get_redis()
    
    if cursor is None:
        print("Не удалось подключиться к PostgreSQL")
        exit(1)
    
    try:
        command = "-1"
        while command != "0":
            command = input("Введите номер задания {3.1, 3.2, 3.3, 3.4, summary, 0 для выхода}: ").strip()
            
            if command == "3.1":
                task_03_01(cursor, redis_client)
            elif command == "3.2":
                task_03_02(cursor, redis_client)
            elif command == "3.3":
                task_03_03(cursor, redis_client)
            elif command == "3.4":
                task_03_04(cursor, redis_client)
            elif command == "summary":
                generate_summary_report()
            elif command == "0":
                print("Выход.")
            else:
                print("Неизвестная команда")
    
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if cursor:
            cursor.close()
            cursor.connection.close()
        print("Соединения закрыты")
