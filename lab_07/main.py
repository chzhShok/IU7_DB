import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *
from link_to_object import LINQToObject
from link_to_json import LINQToJSON
from link_to_sql import LINQToSQL


def to_pandas_df(data, columns=None):
    if isinstance(data, list) and len(data) > 0:
        if columns is None:
            if hasattr(data[0], '__table__'):
                columns = [col.name for col in data[0].__table__.columns]
                rows = [[getattr(item, col) for col in columns] for item in data]
            else:
                if isinstance(data[0], tuple):
                    columns = columns or [f'col_{i}' for i in range(len(data[0]))]
                    rows = data
                elif isinstance(data[0], dict):
                    columns = columns or list(data[0].keys())
                    rows = [[item.get(col) for col in columns] for item in data]
                else:
                    columns = columns or ['value']
                    rows = [[item] for item in data]
        else:
            rows = data

        df = pd.DataFrame(rows, columns=columns)
    else:
        df = pd.DataFrame()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    return df


def menu():
    menu_text = "\n--------- МЕНЮ ------------------------\n" \
                "--------- LINQ_to_Object -------------- \n" \
                "\t1. Вывести премиум пользователей\n" \
                "\t2. Популярность фильмов\n" \
                "\t3. Объединение пользователей и устройств\n" \
                "\t4. Агрегатные данные по пользователям\n" \
                "\t5. Пользователи и их активность\n" \
                "--------- LINQ_to_JSON ---------------- \n" \
                "\t6. Создание JSON документа из БД\n" \
                "\t7. Чтение из JSON документа\n" \
                "\t8. Обновление JSON документа\n" \
                "\t9. Добавление в JSON документ\n" \
                "\t16. Топ фильмов для телефона\n" \
                "--------- LINQ_to_SQL ----------------- \n" \
                "\t10. Активные устройства с недавней активностью\n" \
                "\t11. История просмотров (просмотрено >70%)\n" \
                "\t12. Добавление нового пользователя\n" \
                "\t13. Обновление типа подписки пользователя\n" \
                "\t14. Удаление пользователя\n" \
                "\t15. Средние рейтинги режиссеров\n" \
                "--------------------------------------- \n" \
                "\t0. Выход \n\n"
    print(menu_text)


def main():
    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/streaming_service',
        pool_pre_ping=True
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    linq_json = LINQToJSON(session)
    linq_sql = LINQToSQL(session)

    while True:
        menu()
        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            print("\n=== Премиум пользователи ===")
            users = session.query(Users).all()
            linq_obj = LINQToObject(users)
            result = linq_obj.premium_users_info()
            df = to_pandas_df(result, columns=['full_name', 'email'])
            print(df)

        elif choice == "2":
            print("\n=== Анализ популярности фильмов ===")
            movies = session.query(Movies).all()
            viewing_history = session.query(ViewingHistory).all()
            linq_obj = LINQToObject(movies_data=movies, viewing_history_data=viewing_history)
            result = linq_obj.movie_popularity()

            if result:
                df = to_pandas_df(result)
                print(df)
            else:
                print("Нет данных для анализа")

        elif choice == "3":
            print("\n=== Пользователи и их устройства ===")
            users = session.query(Users).all()
            devices = session.query(Devices).all()
            linq_obj = LINQToObject(users, devices)
            result = linq_obj.join_users_devices()

            join_data = []
            for user, device in result:
                join_data.append({
                    'user_name': user.full_name,
                    'user_email': user.email,
                    'device_name': device.device_name,
                    'device_type': device.device_type
                })
            df = to_pandas_df(join_data)
            print(df)

        elif choice == "4":
            print("\n=== Агрегатные данные ===")
            users = session.query(Users).all()
            view_history = session.query(ViewingHistory).all()
            linq_obj = LINQToObject(users, view_history)
            result = linq_obj.aggregate_users()

            agg_data = [{
                'total_users': result['total_users'],
                'premium_users': result['premium_users'],
                'basic_users': result['total_users'] - result['premium_users'],
                'avg_registration_year': round(result['avg_registration_year'], 1)
            }]
            df = to_pandas_df(agg_data)
            print(df)

        elif choice == "5":
            print("\n=== Комплексный анализ активности пользователей ===")
            users = session.query(Users).all()
            viewing_history = session.query(ViewingHistory).all()
            linq_obj = LINQToObject(users, viewing_history_data=viewing_history)
            result = linq_obj.users_activity()

            if result:
                df = to_pandas_df(result)
                print(df)
            else:
                print("Нет данных для анализа")

        elif choice == "6":
            print("\n=== Создание JSON документа с фильмами ===")
            json_data = linq_json.create_json_document()
            df = to_pandas_df(json_data)
            print(df)
            print(f"\nСоздан JSON документ с {len(json_data)} фильмами")
            print("Файл: movies_data.json")

        elif choice == "7":
            print("\n=== Чтение и анализ JSON с фильмами ===")
            results = linq_json.read_json_document()
            if 'error' in results:
                print(f"  Ошибка: {results['error']}")
            else:
                print("=== Фильмы с высоким рейтингом IMDB (>7.5) ===")
                df_high_rated = to_pandas_df(results['high_rated_movies'])
                print(df_high_rated)
                print("\n=== Популярные фильмы (popularity_score > 50) ===")
                df_popular = to_pandas_df(results['popular_movies'])
                print(df_popular)
                print("\n=== Фильмы с высокой completion rate (>80%) ===")
                df_completion = to_pandas_df(results['high_completion_movies'])
                print(df_completion)

                print("\n=== Статистика по жанрам ===")
                genre_stats = []
                for genre, movies in results['grouped_by_genre'].items():
                    genre_stats.append({
                        'genre': genre,
                        'movie_count': len(movies),
                        'avg_rating': round(sum(m['imdb_rating'] for m in movies if m['imdb_rating']) / len(movies), 2) if movies else 0
                    })
                df_genres = to_pandas_df(genre_stats)
                print(df_genres)

        elif choice == "8":
            print("\n=== Обновление данных фильма в JSON ===")
            try:
                movie_id = int(input("  Введите ID фильма для обновления: "))
                new_rating = float(input("  Введите новый рейтинг IMDB: "))
                success = linq_json.update_json_document(movie_id, {'imdb_rating': new_rating})
                print("  JSON документ успешно обновлен" if success else "  Ошибка при обновлении JSON")
            except ValueError:
                print("  Ошибка: введите корректные данные")

        elif choice == "9":
            print("\n=== Добавление фильма в JSON ===")
            try:
                movie_id = int(input("  Введите ID нового фильма: "))
                title = input("  Введите название фильма: ")
                director = input("  Введите режиссера: ")
                release_year = int(input("  Введите год выпуска: "))
                genres = input("  Введите жанры (через запятую): ")
                new_movie = {
                    'movie_id': movie_id,
                    'title': title,
                    'director': director,
                    'release_year': release_year,
                    'genres': genres,
                    'duration_minutes': 120,
                    'imdb_rating': 0.0,
                    'total_views': 0,
                    'avg_viewed_percentage': 0,
                    'completion_rate': 0,
                    'popularity_score': 0
                }

                success = linq_json.add_to_json_document(new_movie)
                print("  Фильм успешно добавлен в JSON" if success else "  Ошибка при добавлении в JSON")
            except ValueError:
                print("  Ошибка: введите корректные данные")

        elif choice == "10":
            print("\n=== Активные устройства с недавней активностью ===")
            users = linq_sql.single_table_select_active_devices()
            df = to_pandas_df(users)
            print(df)

        elif choice == "11":
            print("\n=== История просмотров (просмотрено >70%) ===")
            results = linq_sql.multi_table_select()

            history_data = []
            for view_history, user_name, movie_title, device_name in results:
                history_data.append({
                    'user_name': user_name,
                    'movie_title': movie_title,
                    'device_name': device_name,
                    'viewed_percentage': view_history.viewed_percentage,
                    'start_time': view_history.start_time
                })

            df = to_pandas_df(history_data)
            print(df)

        elif choice == "12":
            print("\n=== Добавление пользователя в БД ===")
            email = input("  Введите email: ")
            password = input("  Введите пароль (хэш): ")
            full_name = input("  Введите полное имя: ")
            subscription = input("  Введите тип подписки (basic/standard/premium): ")
            user_id = linq_sql.add_user(email, password, full_name, subscription)
            print(f"  Пользователь добавлен с ID: {user_id}")

        elif choice == "13":
            print("\n=== Обновление подписки пользователя ===")
            try:
                user_id = int(input("  Введите ID пользователя: "))
                new_subscription = input("  Введите новый тип подписки: ")
                success = linq_sql.update_user_subscription(user_id, new_subscription)
                print("  Подписка успешно обновлена" if success else "  Пользователь не найден")
            except ValueError:
                print("  Ошибка: введите корректный ID")

        elif choice == "14":
            print("\n=== Удаление пользователя из БД ===")
            try:
                user_id = int(input("  Введите ID пользователя для удаления: "))
                success = linq_sql.delete_user(user_id)
                print("  Пользователь успешно удален" if success else "  Пользователь не найден")
            except ValueError:
                print("  Ошибка: введите корректный ID")

        elif choice == "15":
            print("\n=== Средние рейтинги режиссеров ===")
            director_ratings = linq_sql.execute_stored_procedure()

            if director_ratings:
                df = to_pandas_df(director_ratings)
                print(df)
            else:
                print("Данные не найдены или произошла ошибка")

        elif choice == "16":
            print("\n=== Топ фильмов для просмотра на телефоне ===")

            limit = input("  Введите количество фильмов для вывода (по умолчанию 10): ").strip()
            limit = int(limit) if limit else 10

            top_phone_movies = linq_json.get_top_phone_movies(limit)

            print(f"\n=== Топ-{len(top_phone_movies)} фильмов для телефона ===")
            df = to_pandas_df(top_phone_movies)
            print(df)

        elif choice == "0":
            print("Выход из программы")
            break

        else:
            print("Неверный выбор")

    session.close()


if __name__ == "__main__":
    main()
