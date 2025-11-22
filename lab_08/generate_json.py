import json
import os
import time
from datetime import datetime
import uuid
import random
import psycopg2
from datetime import timedelta


class CinemaDataGenerator:
    def __init__(self, output_dir="../nifi/in_file"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.db_params = {
            'host': 'localhost',
            'database': 'streaming_service',
            'user': 'postgres',
            'password': 'postgres',
            'port': '5432'
        }

        self.tables = ['users', 'movies', 'devices', 'payment_methods', 'viewing_history']

    def get_next_ids(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(user_id) FROM cinema.users")
            max_user_id = cursor.fetchone()[0] or 0

            cursor.execute("SELECT MAX(movie_id) FROM cinema.movies")
            max_movie_id = cursor.fetchone()[0] or 0

            cursor.execute("SELECT MAX(device_id) FROM cinema.devices")
            max_device_id = cursor.fetchone()[0] or 0

            cursor.execute("SELECT MAX(payment_method_id) FROM cinema.payment_methods")
            max_payment_method_id = cursor.fetchone()[0] or 0

            cursor.execute("SELECT MAX(view_id) FROM cinema.viewing_history")
            max_view_id = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            return {
                'users': max_user_id + 1,
                'movies': max_movie_id + 1,
                'devices': max_device_id + 1,
                'payment_methods': max_payment_method_id + 1,
                'viewing_history': max_view_id + 1
            }

        except Exception as e:
            print(f"Error getting next IDs: {e}")
            return {table: 1 for table in self.tables}

    def generate_users_data(self, start_id, num_records=2):
        data = []
        domains = ['gmail.com', 'mail.ru', 'yandex.ru', 'yahoo.com']
        subscription_types = ['basic', 'standard', 'premium']
        names = ['Иван Иванов', 'Петр Петров', 'Мария Сидорова', 'Анна Козлова', 'Сергей Смирнов', 'Ольга Орлова', 'Дмитрий Волков', 'Екатерина Новикова']

        for i in range(num_records):
            name = random.choice(names)
            username = name.lower().replace(' ', '.')
            domain = random.choice(domains)

            user = {
                "user_id": start_id + i,
                "email": f"{username}{random.randint(10, 99)}@{domain}",
                "password_hash": f"hash_{uuid.uuid4().hex[:16]}",
                "full_name": name,
                "registration_date": datetime.now().date().isoformat(),
                "subscription_type": random.choice(subscription_types),
            }
            data.append(user)
        return data

    def generate_movies_data(self, start_id, num_records=3):
        data = []
        titles = ["Последний рассвет", "Тайна океана", "Город теней", "Путь героя", "Эхо прошлого", "Небесный мост"]
        directors = ["Алексей Петров", "Мария Сидорова", "Сергей Иванов", "Анна Козлова"]
        genres = ["Драма, Мелодрама", "Боевик, Триллер", "Комедия, Романтика", "Фантастика, Приключения"]

        for i in range(num_records):
            movie = {
                "movie_id": start_id + i,
                "title": f"{random.choice(titles)} {random.randint(1, 5)}",
                "director": random.choice(directors),
                "release_year": random.randint(2010, 2024),
                "genres": random.choice(genres),
                "duration_minutes": random.randint(80, 180),
                "imdb_rating": round(random.uniform(5.0, 9.5), 1),
            }
            data.append(movie)
        return data

    def generate_devices_data(self, start_id, num_records=4):
        data = []
        device_types = ['smarttv', 'phone', 'tablet', 'pc', 'console']
        device_names = {
            'smarttv': ['Samsung Smart TV', 'LG Smart TV', 'Sony Bravia'],
            'phone': ['iPhone 14', 'Samsung Galaxy S23', 'Google Pixel 7'],
            'tablet': ['iPad Pro', 'Samsung Galaxy Tab', 'Surface Pro'],
            'pc': ['MacBook Pro', 'Dell XPS', 'HP Spectre'],
            'console': ['PlayStation 5', 'Xbox Series X', 'Nintendo Switch']
        }

        user_ids = self.get_existing_user_ids()
        if not user_ids:
            user_ids = [1, 2, 3]

        for i in range(num_records):
            device_type = random.choice(device_types)
            device = {
                "device_id": start_id + i,
                "user_id": random.choice(user_ids),
                "device_type": device_type,
                "device_name": random.choice(device_names[device_type]),
                "last_login_date": datetime.now().date().isoformat(),
                "app_version": f"{random.randint(1, 10)}.{random.randint(1, 10)}.{random.randint(1, 10)}",
                "is_active": random.choice([True, False]),
            }
            data.append(device)
        return data

    def generate_payment_methods_data(self, start_id, num_records=3):
        data = []
        method_types = ['credit card', 'debit card', 'paypal', 'google pay', 'apple pay']

        user_ids = self.get_existing_user_ids()
        if not user_ids:
            user_ids = [1, 2, 3]

        for i in range(num_records):
            method_type = random.choice(method_types)
            payment_data = {
                "payment_method_id": start_id + i,
                "user_id": random.choice(user_ids),
                "method_type": method_type,
                "is_default": random.choice([True, False]),
                "added_date": datetime.now().date().isoformat(),
            }

            if method_type in ['credit card', 'debit card']:
                payment_data["card_last_digits"] = random.randint(1000, 9999)
                expiry_date = datetime.now() + timedelta(days=random.randint(100, 1000))
                payment_data["expiry_date"] = expiry_date.date().isoformat()

            data.append(payment_data)
        return data

    def generate_viewing_history_data(self, start_id, num_records=5):
        data = []

        user_ids = self.get_existing_user_ids()
        movie_ids = self.get_existing_movie_ids()
        device_ids = self.get_existing_device_ids()

        if not user_ids or not movie_ids or not device_ids:
            return data

        for i in range(num_records):
            view = {
                "view_id": start_id + i,
                "user_id": random.choice(user_ids),
                "movie_id": random.choice(movie_ids),
                "device_id": random.choice(device_ids),
                "viewed_percentage": random.randint(10, 100),
            }
            data.append(view)
        return data

    def get_existing_user_ids(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM cinema.users LIMIT 10")
            user_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return user_ids
        except:
            return [1, 2, 3]

    def get_existing_movie_ids(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("SELECT movie_id FROM cinema.movies LIMIT 10")
            movie_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return movie_ids
        except:
            return [1, 2, 3]

    def get_existing_device_ids(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("SELECT device_id FROM cinema.devices LIMIT 10")
            device_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return device_ids
        except:
            return [1, 2, 3]

    def generate_filename(self, table_name, file_format):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        return f"{file_id}_{table_name}_{timestamp}.{file_format}"

    def save_json(self, data, filename):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def run_generator(self):
        format = 'json'
        record_counts = {
            'users': (1, 3),
            'movies': (1, 4),
            'devices': (1, 5),
            'payment_methods': (1, 4),
            'viewing_history': (1, 6)
        }

        while True:
            try:
                next_ids = self.get_next_ids()

                table_name = random.choice(self.tables)
                file_format = format

                min_rec, max_rec = record_counts[table_name]
                num_records = random.randint(min_rec, max_rec)
                start_id = next_ids[table_name]

                if table_name == 'users':
                    data = self.generate_users_data(start_id, num_records)
                elif table_name == 'movies':
                    data = self.generate_movies_data(start_id, num_records)
                elif table_name == 'devices':
                    data = self.generate_devices_data(start_id, num_records)
                elif table_name == 'payment_methods':
                    data = self.generate_payment_methods_data(start_id, num_records)
                else:
                    data = self.generate_viewing_history_data(start_id, num_records)

                filename = self.generate_filename(table_name, file_format)

                self.save_json(data, filename)

                print(f"Generated: {filename} with {len(data)} records for table {table_name}")

                time.sleep(10)

            except Exception as e:
                print(f"Error in generator: {e}")
                time.sleep(60)


if __name__ == "__main__":
    generator = CinemaDataGenerator()
    generator.run_generator()
