from models import Movies, ViewingHistory
from collections import defaultdict
import json


class LINQToJSON:
    def __init__(self, session):
        self.session = session

    def create_json_document(self):
        """Создание JSON документа с данными о фильмах и их статистикой просмотров"""
        movies_data = self.session.query(Movies).all()

        json_data = []
        for movie in movies_data:
            # Получаем статистику просмотров для фильма
            viewing_stats = self.session.query(ViewingHistory).filter(
                ViewingHistory.movie_id == movie.movie_id
            ).all()

            # Вычисляем метрики
            total_views = len(viewing_stats)
            avg_viewed_percentage = sum(vh.viewed_percentage for vh in viewing_stats) / total_views if total_views > 0 else 0
            completed_views = len([vh for vh in viewing_stats if vh.viewed_percentage >= 90])

            movie_dict = {
                'movie_id': movie.movie_id,
                'title': movie.title,
                'director': movie.director,
                'release_year': movie.release_year,
                'genres': movie.genres,
                'duration_minutes': movie.duration_minutes,
                'imdb_rating': float(movie.imdb_rating) if movie.imdb_rating else None,
                'total_views': total_views,
                'avg_viewed_percentage': round(avg_viewed_percentage, 1),
                'completion_rate': round((completed_views / total_views * 100) if total_views > 0 else 0, 1),
                'popularity_score': round(total_views * avg_viewed_percentage / 100, 2) if total_views > 0 else 0
            }
            json_data.append(movie_dict)

        with open('movies_data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return json_data

    def read_json_document(self):
        try:
            with open('movies_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            high_rated_movies = [movie for movie in data if movie['imdb_rating'] and movie['imdb_rating'] > 7.5]

            grouped_by_genre = defaultdict(list)
            for movie in data:
                if movie['genres']:
                    genres = [genre.strip() for genre in movie['genres'].split(',')]
                    for genre in genres:
                        grouped_by_genre[genre].append(movie)

            popular_movies = [movie for movie in data if movie['popularity_score'] > 50]

            high_completion_movies = [movie for movie in data if movie['completion_rate'] > 80]

            return {
                'high_rated_movies': high_rated_movies,
                'grouped_by_genre': dict(grouped_by_genre),
                'popular_movies': popular_movies,
                'high_completion_movies': high_completion_movies
            }
        except FileNotFoundError:
            return {"error": "JSON файл не найден"}

    def update_json_document(self, movie_id, updates):
        try:
            with open('movies_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            for movie in data:
                if movie['movie_id'] == movie_id:
                    movie.update(updates)
                    break

            with open('movies_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except FileNotFoundError:
            return False

    def add_to_json_document(self, new_movie):
        try:
            with open('movies_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            data.append(new_movie)

            with open('movies_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except FileNotFoundError:
            return False
