import random
from datetime import datetime, timedelta, date

def generate_devices_data(users_data, num_devices_per_user=2):
    devices_data = []
    device_id_counter = 1
    
    device_types = {
        'phone': ['iPhone 14', 'iPhone 13', 'iPhone 12', 'Samsung Galaxy S23', 'Samsung Galaxy S22', 
                  'Google Pixel 7', 'OnePlus 11', 'Xiaomi 13', 'Huawei P50', 'iPhone 15'],
        'tablet': ['iPad Pro', 'iPad Air', 'iPad', 'Samsung Galaxy Tab S8', 'Samsung Galaxy Tab S7',
                  'Google Pixel Tablet', 'Amazon Fire HD', 'Lenovo Tab P11', 'Surface Pro 9'],
        'smarttv': ['Samsung Smart TV', 'LG Smart TV', 'Sony Bravia', 'TCL Smart TV', 'Hisense Smart TV',
                    'Vizio Smart TV', 'Roku TV', 'Android TV', 'Apple TV 4K', 'Fire TV'],
        'pc': ['MacBook Pro', 'MacBook Air', 'Dell XPS', 'HP Spectre', 'Lenovo ThinkPad',
               'ASUS ZenBook', 'Surface Laptop', 'Acer Swift', 'MSI Creator', 'Razer Blade',
               'Custom PC', 'iMac', 'Dell OptiPlex', 'HP Pavilion', 'Lenovo ThinkCentre',
               'ASUS ROG', 'Alienware Aurora', 'Mac Studio', 'Surface Studio'],
        'console': ['PlayStation 5', 'Xbox Series X', 'Nintendo Switch', 'PlayStation 4',
                    'Xbox One', 'Steam Deck', 'Nintendo Switch OLED', 'PlayStation 4 Pro',
                    'Roku Ultra', 'Amazon Fire Stick', 'Google Chromecast', 'Apple TV',
                    'NVIDIA Shield', 'Roku Express', 'Fire TV Cube', 'Chromecast Ultra']
    }
    
    for user in users_data:
        user_id = user['user_id']
        reg_date = user['registration_date']
                
        num_devices = random.choices(
            [1, 2, 3, 4], 
            weights=[0.1, 0.4, 0.4, 0.1], 
            k=1
        )[0]
        
        used_device_types = set()
        
        for i in range(num_devices):
            available_types = [dt for dt in device_types.keys() if dt not in used_device_types]
            if not available_types:
                available_types = list(device_types.keys())
            
            device_type = random.choice(available_types)
            used_device_types.add(device_type)
            
            device_name = random.choice(device_types[device_type])
            app_version = generate_app_version()
            days_since_reg = (date.today() - reg_date).days
            is_active = random.random() < 0.85
            
            if is_active:
                days_ago = random.randint(0, min(30, days_since_reg))
                last_login_date = date.today() - timedelta(days=days_ago)
            else:
                if random.random() < 0.3:
                    last_login_date = None
                else:
                    min_days = min(31, days_since_reg)
                    max_days = min(365, days_since_reg)
                    if min_days <= max_days:
                        days_ago = random.randint(min_days, max_days)
                        last_login_date = date.today() - timedelta(days=days_ago)
                    else:
                        days_ago = random.randint(0, days_since_reg)
                        last_login_date = date.today() - timedelta(days=days_ago)
                        
            devices_data.append({
                'device_id': device_id_counter,
                'user_id': user_id,
                'device_type': device_type,
                'device_name': device_name,
                'last_login_date': last_login_date,
                'app_version': app_version,
                'is_active': is_active,
            })
            
            device_id_counter += 1
    
    return devices_data

def generate_app_version():
    return f"{random.randint(1, 10)}.{random.randint(1, 10)}.{random.randint(1, 10)}"

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
    
    devices = generate_devices_data(sample_users, num_devices_per_user=2)
    print(devices)
