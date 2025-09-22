import csv
import random
from datetime import datetime, timedelta
import os

def generate_movies_data(num_records=1000):
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Movies CSV file not found at: {csv_file_path}")
    
    movies_data = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        all_movies = list(reader)
    
    if len(all_movies) == 0:
        raise ValueError("No movies found in CSV file")
    
    if num_records > len(all_movies):
        num_records = len(all_movies)
        print(f"Warning: Requested {num_records} movies, but only {len(all_movies)} available. Using all available movies.")
    
    selected_movies = random.sample(all_movies, num_records)
    
    movie_id_counter = 1
    for movie in selected_movies:
        try:
            title = movie.get('title', '').strip()
            director = movie.get('director', '').strip()
            
            release_year = movie.get('release_year')
            if release_year == '\\N':
                release_year = None
            else:
                release_year = int(release_year)
            
            duration_minutes = movie.get('duration_minutes')
            if duration_minutes == '\\N':
                duration_minutes = None
            else:
                duration_minutes = int(duration_minutes)
            
            imdb_rating = movie.get('imdb_rating')
            if imdb_rating == '\\N':
                imdb_rating = None
            else:
                imdb_rating = float(imdb_rating)

            genres = movie.get('genres')
            if genres == '\\N':
                genres = None
            else:
                genres = ', '.join([g.strip().lower() for g in movie['genres'].split(',') if g.strip()])
            
            movies_data.append({
                'movie_id': movie_id_counter,
                'title': title,
                'director': director,
                'release_year': release_year,
                'genres': genres,
                'duration_minutes': duration_minutes,
                'imdb_rating': imdb_rating
            })
            
            movie_id_counter += 1
            
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping movie '{movie.get('title', 'Unknown')}' due to data error: {e}")
            continue
    
    return movies_data


if __name__ == "__main__":
    movies = generate_movies_data(1)
    print(movies)
