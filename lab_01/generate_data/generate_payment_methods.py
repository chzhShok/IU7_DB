import random
from datetime import datetime, timedelta

def generate_payment_methods_data(users_data, num_records_per_user=2):
    payment_methods_data = []
    
    method_types = ['credit card', 'debit card', 'paypal', 'google pay', 'apple pay']
    card_methods = ['credit card', 'debit card']
    
    for user in users_data:
        user_id = user['user_id']
        
        num_methods = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        default_set = False
        
        for i in range(num_methods):
            method_type = random.choice(method_types)
            
            if method_type in card_methods:
                card_last_digits = str(random.randint(1000, 9999))
                expiry_date = generate_expiry_date()
            else:
                card_last_digits = None
                expiry_date = None
            
            is_default = not default_set and (i == 0 or random.random() < 0.3)
            if is_default:
                default_set = True
            
            added_date = generate_added_date(user['registration_date'])
            
            payment_methods_data.append({
                'user_id': user_id,
                'method_type': method_type,
                'card_last_digits': card_last_digits,
                'is_default': is_default,
                'added_date': added_date,
                'expiry_date': expiry_date
            })
    
    return payment_methods_data

def generate_expiry_date():
    current_date = datetime.now()
    years = random.randint(1, 5)
    expiry_date = current_date + timedelta(days=365 * years)
    return expiry_date.date()

def generate_added_date(user_registration_date):
    reg_date = user_registration_date
    end_date = datetime.now().date()
    days_since_reg = (end_date - reg_date).days
    
    if days_since_reg <= 0:
        return reg_date

    random_days = random.randint(0, days_since_reg)
    added_date = reg_date + timedelta(days=random_days)
    return added_date

if __name__ == "__main__":
    users_data = [
        {'user_id': 1, 'registration_date': '2024-01-16'}, 
    ]
    payment_methods_data = generate_payment_methods_data(users_data)
    print(payment_methods_data)