class LINQToObject:
    def __init__(self, users_data=None, devices_data=None, viewing_history_data=None, movies_data=None):
        self.users_data = users_data or []
        self.devices_data = devices_data or []
        self.viewing_history_data = viewing_history_data or []
        self.movies_data = movies_data or []

    def premium_users_info(self):
        result = [user for user in self.users_data if user.subscription_type == 'premium']
        return [(user.full_name, user.email) for user in result]

    def movie_popularity(self):
        if not self.viewing_history_data or not self.movies_data:
            return []

        movie_stats = []

        for movie in self.movies_data:
            movie_views = [vh for vh in self.viewing_history_data if vh.movie_id == movie.movie_id]

            if movie_views:
                avg_completion = sum(vh.viewed_percentage for vh in movie_views) / len(movie_views)
                unique_viewers = len(set(vh.user_id for vh in movie_views))
                avg_rating = movie.imdb_rating if movie.imdb_rating else 0

                movie_stats.append({
                    'movie_id': movie.movie_id,
                    'title': movie.title,
                    'director': movie.director,
                    'release_year': movie.release_year,
                    'total_views': len(movie_views),
                    'unique_viewers': unique_viewers,
                    'avg_completion_rate': round(avg_completion, 1),
                    'imdb_rating': avg_rating,
                    'popularity_score': round(len(movie_views) * avg_completion / 100, 1)
                })

        return sorted(movie_stats, key=lambda x: x['popularity_score'], reverse=True)

    def join_users_devices(self):
        if not self.devices_data:
            return []
        return [(user, device) for user in self.users_data
                for device in self.devices_data
                if user.user_id == device.user_id]

    def aggregate_users(self):
        premium_users = sum(1 for user in self.users_data if user.subscription_type == 'premium')
        total_users = len(self.users_data)
        avg_year = (sum(user.registration_date.year for user in self.users_data) / total_users) if total_users > 0 else 0

        return {
            'premium_users': premium_users,
            'total_users': total_users,
            'avg_registration_year': avg_year
        }

    def users_activity(self):
        if not self.viewing_history_data:
            return []

        user_viewing_stats = []

        for user in self.users_data:
            user_views = [vh for vh in self.viewing_history_data if vh.user_id == user.user_id]

            if user_views:
                avg_viewed_percentage = sum(vh.viewed_percentage for vh in user_views) / len(user_views)
                total_viewing_time = sum(
                    (vh.end_time - vh.start_time).total_seconds() / 3600 if vh.end_time else 0
                    for vh in user_views
                )
                unique_movies = len(set(vh.movie_id for vh in user_views))

                user_viewing_stats.append({
                    'user_id': user.user_id,
                    'full_name': user.full_name,
                    'subscription_type': user.subscription_type,
                    'total_views': len(user_views),
                    'unique_movies': unique_movies,
                    'avg_viewed_percentage': round(avg_viewed_percentage, 1),
                    'total_viewing_hours': round(total_viewing_time, 1),
                    'completion_rate': len([vh for vh in user_views if vh.viewed_percentage >= 90]) / len(user_views) * 100
                })

        return sorted(user_viewing_stats, key=lambda x: x['total_viewing_hours'], reverse=True)
