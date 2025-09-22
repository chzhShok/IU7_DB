import random
from datetime import datetime, timedelta, date

def generate_viewing_history_data(users_data, movies_data, devices_data, num_records_per_user=15):
    viewing_history_data = []
    
    user_devices = {}
    for device in devices_data:
        user_id = device['user_id']
        if user_id not in user_devices:
            user_devices[user_id] = []
        user_devices[user_id].append(device)
    
    movie_durations = {movie['movie_id']: movie.get('duration_minutes') or 120 for movie in movies_data}
    
    for user in users_data:
        user_id = user['user_id']
        reg_date = user['registration_date']
        
        user_device_list = user_devices.get(user_id, [])
        active_devices = [d for d in user_device_list if d['is_active']]
        all_devices = user_device_list
        
        if not all_devices:
            continue
        
        days_since_reg = (date.today() - reg_date).days
        if days_since_reg <= 0:
            continue
        
        activity_level = random.choices(['low', 'medium', 'high'], weights=[0.3, 0.5, 0.2])[0]
        
        if activity_level == 'low':
            num_views = random.randint(5, 15)
        elif activity_level == 'medium':
            num_views = random.randint(15, 40)
        else:
            num_views = random.randint(40, 80)
        
        num_views = min(num_views, days_since_reg * 2)
        
        for _ in range(num_views):
            movie = random.choice(movies_data)
            movie_id = movie['movie_id']
            movie_duration = movie_durations.get(movie_id, 120)
            
            if movie_duration is None:
                movie_duration = 120
            
            if random.random() < 0.8 and active_devices:
                device = random.choice(active_devices)
            else:
                device = random.choice(all_devices)
            
            device_id = device['device_id']
            
            start_time = datetime(2024, 1, 1) + timedelta(
                days=random.randint(0, 364),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            viewed_percentage = generate_viewed_percentage()
            
            if viewed_percentage == 100:
                end_time = start_time + timedelta(minutes=movie_duration)
            elif viewed_percentage == 0:
                end_time = start_time + timedelta(minutes=random.randint(1, 5))
            else:
                watched_minutes = int((viewed_percentage / 100) * movie_duration)
                end_time = start_time + timedelta(minutes=watched_minutes)
            
            current_time = datetime.now()
            if end_time > current_time:
                end_time = current_time - timedelta(hours=1)
            
            if end_time <= start_time:
                end_time = start_time + timedelta(minutes=1)
            
            viewing_history_data.append({
                'user_id': user_id,
                'movie_id': movie_id,
                'device_id': device_id,
                'start_time': start_time,
                'end_time': end_time,
                'viewed_percentage': viewed_percentage
            })
    
    viewing_history_data.sort(key=lambda x: x['start_time'])
    
    return viewing_history_data

def generate_viewed_percentage():
    category = random.choices(
        ['complete', 'almost_complete', 'partial', 'abandoned'],
        weights=[0.4, 0.2, 0.15, 0.25]
    )[0]
    
    if category == 'complete':
        return 100
    elif category == 'almost_complete':
        return random.randint(80, 99)
    elif category == 'partial':
        return random.randint(40, 79)
    else:
        return random.randint(0, 39)

if __name__ == "__main__":
    sample_users = [
        {
            'user_id': 1,
            'registration_date': date(2023, 1, 15)
        },
        {
            'user_id': 2,
            'registration_date': date(2024, 6, 10)
        }
    ]
    
    sample_movies = [
        {'movie_id': 1, 'title': 'Movie 1', 'duration_minutes': 120},
        {'movie_id': 2, 'title': 'Movie 2', 'duration_minutes': 90},
        {'movie_id': 3, 'title': 'Movie 3', 'duration_minutes': 150}
    ]
    
    sample_devices = [
        {'device_id': 1, 'user_id': 1, 'is_active': True},
        {'device_id': 2, 'user_id': 1, 'is_active': False},
        {'device_id': 3, 'user_id': 2, 'is_active': True}
    ]
    
    viewing_history = generate_viewing_history_data(sample_users, sample_movies, sample_devices)
    print(f"Generated {len(viewing_history)} viewing history records:")
    for record in viewing_history[:3]:  # Show first 3
        print(f"- User {record['user_id']} watched movie {record['movie_id']} on device {record['device_id']}: {record['viewed_percentage']}% complete")
