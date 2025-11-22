from sqlalchemy import text, func
from datetime import date, timedelta

from models import Users, ViewingHistory, Movies, Devices


class LINQToSQL:
    def __init__(self, session):
        self.session = session

    def single_table_select_active_devices(self):
        thirty_days_ago = date.today() - timedelta(days=30)

        return self.session.query(Devices).filter(
            Devices.is_active == True,
            Devices.last_login_date >= thirty_days_ago
        ).order_by(Devices.last_login_date.desc()).all()

    def multi_table_select(self):
        return self.session.query(
            ViewingHistory,
            Users.full_name,
            Movies.title,
            Devices.device_name
        ).join(Users, ViewingHistory.user_id == Users.user_id) \
            .join(Movies, ViewingHistory.movie_id == Movies.movie_id) \
            .join(Devices, ViewingHistory.device_id == Devices.device_id) \
            .filter(ViewingHistory.viewed_percentage > 70) \
            .all()

    def add_user(self, email, password_hash, full_name, subscription_type='basic'):
        max_id = self.session.query(func.max(Users.user_id)).scalar() or 0
        next_id = max_id + 1

        new_user = Users(
            user_id=next_id,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            subscription_type=subscription_type,
        )
        self.session.add(new_user)
        self.session.commit()
        return new_user.user_id

    def update_user_subscription(self, user_id, new_subscription):
        user = self.session.query(Users).filter(Users.user_id == user_id).first()
        if user:
            user.subscription_type = new_subscription
            self.session.commit()
            return True
        return False

    def delete_user(self, user_id):
        user = self.session.query(Users).filter(Users.user_id == user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def execute_stored_procedure(self):
        try:
            create_proc_sql = """
            CREATE OR REPLACE FUNCTION cinema.get_all_directors_avg_ratings()
            RETURNS TABLE(
                director_name TEXT,
                avg_rating DECIMAL,
                movie_count BIGINT
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    m.director as director_name,
                    ROUND(AVG(m.imdb_rating)::numeric, 2) as avg_rating,
                    COUNT(*) as movie_count
                FROM cinema.movies m
                WHERE m.director IS NOT NULL AND m.imdb_rating IS NOT NULL
                GROUP BY m.director
                ORDER BY avg_rating DESC;
            END;
            $$ LANGUAGE plpgsql;
            """
            self.session.execute(text(create_proc_sql))
            self.session.commit()

            result = self.session.execute(
                text("SELECT * FROM cinema.get_all_directors_avg_ratings()")
            )

            director_ratings = []
            for row in result:
                director_ratings.append({
                    'director': row[0],
                    'avg_rating': float(row[1]) if row[1] else 0.0,
                    'movie_count': row[2]
                })

            return director_ratings
        except Exception as e:
            print(f"Ошибка при выполнении хранимой процедуры: {e}")
            return None
