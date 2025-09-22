from generate_users import generate_users_data
from generate_payment_methods import generate_payment_methods_data
from generate_movies import generate_movies_data
from generate_devices import generate_devices_data
from generate_viewing_history import generate_viewing_history_data

import psycopg2


def truncate_tables(db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        truncate_users_query = """
            TRUNCATE TABLE cinema.users CASCADE;
        """
        truncate_movies_query = """
            TRUNCATE TABLE cinema.movies CASCADE;
        """
        truncate_devices_query = """
            TRUNCATE TABLE cinema.devices CASCADE;
        """
        truncate_payment_methods_query = """
            TRUNCATE TABLE cinema.payment_methods CASCADE;
        """
        truncate_viewing_history_query = """
            TRUNCATE TABLE cinema.viewing_history CASCADE;
        """
        
        cursor.execute(truncate_users_query)
        cursor.execute(truncate_movies_query)
        cursor.execute(truncate_devices_query)
        cursor.execute(truncate_payment_methods_query)
        cursor.execute(truncate_viewing_history_query)
        
        conn.commit()
        print(f"Таблицы успешно очищены")
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()


def insert_users_to_db(users_data, db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO cinema.users 
            (user_id, email, password_hash, full_name, registration_date, subscription_type) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for user in users_data:
            cursor.execute(insert_query, (
                user['user_id'],
                user['email'],
                user['password_hash'],
                user['full_name'],
                user['registration_date'],
                user['subscription_type']
            ))
        
        conn.commit()
        print(f"Успешно добавлено {len(users_data)} пользователей")
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_payment_methods_to_db(payment_methods_data, db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO cinema.payment_methods 
            (user_id, method_type, card_last_digits, is_default, added_date, expiry_date) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for method in payment_methods_data:
            cursor.execute(insert_query, (
                method['user_id'],
                method['method_type'],
                method['card_last_digits'],
                method['is_default'],
                method['added_date'],
                method['expiry_date']
            ))
        
        conn.commit()
        print(f"Успешно добавлено {len(payment_methods_data)} способов оплаты")
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_movies_to_db(movies_data, db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO cinema.movies 
            (title, director, release_year, genres, duration_minutes, imdb_rating) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING movie_id
        """
        
        movie_id_mapping = {}
        for movie in movies_data:
            cursor.execute(insert_query, (
                movie['title'],
                movie['director'],
                movie['release_year'],
                movie['genres'],
                movie['duration_minutes'],
                movie['imdb_rating'],
            ))
            db_movie_id = cursor.fetchone()[0]
            movie_id_mapping[movie['movie_id']] = db_movie_id
        
        conn.commit()
        print(f"Успешно добавлено {len(movies_data)} фильмов")
        return movie_id_mapping
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
        return {}
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_devices_to_db(devices_data, db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO cinema.devices 
            (user_id, device_type, device_name, last_login_date, app_version, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING device_id
        """
        
        device_id_mapping = {}
        for device in devices_data:
            cursor.execute(insert_query, (
                device['user_id'],
                device['device_type'],
                device['device_name'],
                device['last_login_date'],
                device['app_version'],
                device['is_active'],
            ))
            db_device_id = cursor.fetchone()[0]
            device_id_mapping[device['device_id']] = db_device_id
        
        conn.commit()
        print(f"Успешно добавлено {len(devices_data)} устройств")
        return device_id_mapping
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
        return {}
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_viewing_history_to_db(viewing_history_data, movie_id_mapping, device_id_mapping, db_params):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO cinema.viewing_history 
            (user_id, movie_id, device_id, start_time, end_time, viewed_percentage) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for record in viewing_history_data:
            db_movie_id = movie_id_mapping.get(record['movie_id'])
            db_device_id = device_id_mapping.get(record['device_id'])
            
            if db_movie_id is None or db_device_id is None:
                print(f"Warning: Skipping viewing record - movie_id {record['movie_id']} or device_id {record['device_id']} not found in mapping")
                continue
                
            cursor.execute(insert_query, (
                record['user_id'],
                db_movie_id,
                db_device_id,
                record['start_time'],
                record['end_time'],
                record['viewed_percentage']
            ))
        
        conn.commit()
        print(f"Успешно добавлено {len(viewing_history_data)} записей истории просмотров")
        
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    db_params = {
        'host': 'localhost',
        'database': 'streaming_service',
        'user': 'postgres',
        'password': 'postgres',
        'port': '5432'
    }

    response = input("\nОчистить таблицы? (y/n): ")
    if response.lower() == 'y':
        truncate_tables(db_params)
    
    data_count = 1000

    users_data = generate_users_data(data_count)
    payment_methods_data = generate_payment_methods_data(users_data)
    movies_data = generate_movies_data(data_count)
    devices_data = generate_devices_data(users_data)
    viewing_history_data = generate_viewing_history_data(users_data, movies_data, devices_data)
    
    response = input("\nВставить данные в базу? (y/n): ")
    if response.lower() == 'y':
        insert_users_to_db(users_data, db_params)
        insert_payment_methods_to_db(payment_methods_data, db_params)
        movie_id_mapping = insert_movies_to_db(movies_data, db_params)
        device_id_mapping = insert_devices_to_db(devices_data, db_params)
        insert_viewing_history_to_db(viewing_history_data, movie_id_mapping, device_id_mapping, db_params)
    else:
        print("Данные не были вставлены в базу")

if __name__ == "__main__":
    main()
