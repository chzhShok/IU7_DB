from faker import Faker
import random
from datetime import datetime, timedelta
import hashlib
from transliterate import translit

def generate_users_data(num_records=1000):
    fake = Faker('ru_RU')
    users_data = []
    used_emails = set()
    
    subscription_types = ['basic', 'standard', 'premium']
    
    for i in range(num_records):
        full_name = fake.name()
        email = generate_unique_email(full_name, used_emails)
        password_hash = generate_password_hash()
        registration_date = generate_registration_date()
        subscription_type = random.choice(subscription_types)
        
        users_data.append({
            'user_id': i + 1,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'registration_date': registration_date,
            'subscription_type': subscription_type
        })
    
    return users_data

def generate_unique_email(full_name, used_emails):
    while True:
        email = generate_email(full_name)
        if email not in used_emails:
            used_emails.add(email)
            return email

def generate_email(full_name):
    full_name_english = translit(full_name, language_code='ru', reversed=True)
    name_parts = full_name_english.lower().split()
    
    if len(name_parts) < 2:
        name_parts = ['user', 'name']
    
    domains = ['gmail.com', 'mail.ru', 'yandex.ru', 'yahoo.com', 'icloud.com']
    
    formats = [
        f"{name_parts[0]}.{name_parts[1]}",
        f"{name_parts[0][0]}.{name_parts[1]}",
        f"{name_parts[0]}_{name_parts[1]}",
        f"{name_parts[0]}{random.randint(10, 99)}",
        f"{name_parts[1]}{random.randint(1970, 2005)}"
    ]
    
    username = random.choice(formats)
    domain = random.choice(domains)
    
    return f"{username}@{domain}"

def generate_password_hash():
    password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
    return hashlib.sha256(password.encode()).hexdigest()

def generate_registration_date():
    end_date = datetime.now()
    start_date = datetime(2020, 1, 1)
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    
    return random_date.date()

if __name__ == '__main__':
    data = generate_users_data()
    print(data[0])