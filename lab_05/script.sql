-- 1. извлечь данные в json из всех таблиц
copy (
    select json_agg(row_to_json(users)) 
    from cinema.users
) to '/tmp/users.json';

copy (
    select json_agg(row_to_json(movies)) 
    from cinema.movies
) to '/tmp/movies.json';

copy (
    select json_agg(row_to_json(devices)) 
    from cinema.devices
) to '/tmp/devices.json';

copy (
    select json_agg(row_to_json(payment_methods)) 
    from cinema.payment_methods
) to '/tmp/payment_methods.json';

copy (
    select json_agg(row_to_json(viewing_history)) 
    from cinema.viewing_history
) to '/tmp/viewing_history.json';

-- 2. загружаем данные из json
truncate table cinema.viewing_history cascade;
truncate table cinema.payment_methods cascade;
truncate table cinema.devices cascade;
truncate table cinema.movies cascade;
truncate table cinema.users cascade;

insert into cinema.users (
    user_id, 
    email, 
    password_hash, 
    full_name, 
    registration_date, 
    subscription_type, 
    created_at
)
select 
    (json_data->>'user_id')::integer,
    json_data->>'email',
    json_data->>'password_hash',
    json_data->>'full_name',
    (json_data->>'registration_date')::date,
    json_data->>'subscription_type',
    (json_data->>'created_at')::timestamp
from (
    select json_array_elements(json_data) as json_data
    from (
        select json_data::json
        from pg_catalog.pg_ls_dir('/tmp') as files
        cross join lateral pg_catalog.pg_read_file('/tmp/users.json') as json_data
        where files = 'users.json'
    ) as file_data
) as users_data;

insert into cinema.movies (
    movie_id,
    title,
    director,
    release_year,
    genres,
    duration_minutes,
    imdb_rating,
    created_at
)
select 
    (json_data->>'movie_id')::integer,
    json_data->>'title',
    json_data->>'director',
    (json_data->>'release_year')::integer,
    json_data->>'genres',
    (json_data->>'duration_minutes')::integer,
    (json_data->>'imdb_rating')::decimal(2,1),
    (json_data->>'created_at')::timestamp
from (
    select json_array_elements(json_data) as json_data
    from (
        select json_data::json
        from pg_catalog.pg_ls_dir('/tmp') as files
        cross join lateral pg_catalog.pg_read_file('/tmp/movies.json') as json_data
        where files = 'movies.json'
    ) as file_data
) as movies_data;

insert into cinema.devices (
    device_id,
    user_id,
    device_type,
    device_name,
    last_login_date,
    app_version,
    is_active,
    created_at
)
select 
    (json_data->>'device_id')::integer,
    (json_data->>'user_id')::integer,
    json_data->>'device_type',
    json_data->>'device_name',
    (json_data->>'last_login_date')::date,
    json_data->>'app_version',
    (json_data->>'is_active')::boolean,
    (json_data->>'created_at')::timestamp
from (
    select json_array_elements(json_data) as json_data
    from (
        select json_data::json
        from pg_catalog.pg_ls_dir('/tmp') as files
        cross join lateral pg_catalog.pg_read_file('/tmp/devices.json') as json_data
        where files = 'devices.json'
    ) as file_data
) as devices_data;

insert into cinema.payment_methods (
    payment_method_id,
    user_id,
    method_type,
    card_last_digits,
    is_default,
    added_date,
    expiry_date,
    created_at
)
select 
    (json_data->>'payment_method_id')::integer,
    (json_data->>'user_id')::integer,
    json_data->>'method_type',
    (json_data->>'card_last_digits')::decimal(4,0),
    (json_data->>'is_default')::boolean,
    (json_data->>'added_date')::date,
    (json_data->>'expiry_date')::date,
    (json_data->>'created_at')::timestamp
from (
    select json_array_elements(json_data) as json_data
    from (
        select json_data::json
        from pg_catalog.pg_ls_dir('/tmp') as files
        cross join lateral pg_catalog.pg_read_file('/tmp/payment_methods.json') as json_data
        where files = 'payment_methods.json'
    ) as file_data
) as payment_methods_data;

insert into cinema.viewing_history (
    view_id,
    user_id,
    movie_id,
    device_id,
    start_time,
    end_time,
    viewed_percentage,
    created_at
)
select 
    (json_data->>'view_id')::integer,
    (json_data->>'user_id')::integer,
    (json_data->>'movie_id')::integer,
    (json_data->>'device_id')::integer,
    (json_data->>'start_time')::timestamp,
    (json_data->>'end_time')::timestamp,
    (json_data->>'viewed_percentage')::integer,
    (json_data->>'created_at')::timestamp
from (
    select json_array_elements(json_data) as json_data
    from (
        select json_data::json
        from pg_catalog.pg_ls_dir('/tmp') as files
        cross join lateral pg_catalog.pg_read_file('/tmp/viewing_history.json') as json_data
        where files = 'viewing_history.json'
    ) as file_data
) as viewing_history_data;

select setval('cinema.users_user_id_seq', (select coalesce(max(user_id), 1) from cinema.users));
select setval('cinema.movies_movie_id_seq', (select coalesce(max(movie_id), 1) from cinema.movies));
select setval('cinema.devices_device_id_seq', (select coalesce(max(device_id), 1) from cinema.devices));
select setval('cinema.payment_methods_payment_method_id_seq', (select coalesce(max(payment_method_id), 1) from cinema.payment_methods));
select setval('cinema.viewing_history_view_id_seq', (select coalesce(max(view_id), 1) from cinema.viewing_history));

-- 3. добавить json атрибут к существующей таблице
alter table cinema.users add column preferences jsonb;

update cinema.users 
set preferences = '{
    "language": "english",
    "subtitles": true,
    "quality": "hd",
    "autoplay": true,
    "notifications": {
        "email": true,
        "push": false,
        "sms": true
    },
    "favorite_genres": ["action", "drama", "sci-fi"]
}'::jsonb
where user_id = 1;

update cinema.users 
set preferences = '{
    "language": "russian",
    "subtitles": false,
    "quality": "full_hd",
    "autoplay": false,
    "notifications": {
        "email": false,
        "push": true,
        "sms": false
    },
    "favorite_genres": ["comedy", "romance"]
}'::jsonb
where user_id = 2;

select preferences from cinema.users u where u.user_id = 1;

-- 4. выполняем различные операции с json

-- 4.1 извлечь json фрагмент из json документа
select 
    user_id,
    email,
    preferences->'notifications' as notifications_settings
from cinema.users;

-- 4.2 извлечь значения конкретных узлов или атрибутов json
select 
    user_id,
    full_name,
    preferences->>'language' as preferred_language,
    preferences->'notifications'->>'email' as email_notifications,
    preferences->'favorite_genres'->>0 as primary_genre
from cinema.users;

-- 4.3 выполнить проверку существования узла или атрибута
select 
    user_id,
    email,
    preferences ? 'notifications' as has_notifications,
    preferences->'notifications' ? 'push' as has_push_notifications,
    jsonb_path_exists(preferences, '$.favorite_genres[*] ? (@ == "action")') as likes_action
from cinema.users;

-- 4.4 изменить json документ
update cinema.users 
set preferences = jsonb_set(
    preferences, 
    '{parental_control}', 
    '{"enabled": true, "level": "pg13"}'::jsonb
)
where user_id = 1;

select u.preferences from cinema.users u where u.user_id = 1;

update cinema.users 
set preferences = jsonb_set(
    preferences, 
    '{quality}', 
    '"4k"'::jsonb
)
where user_id = 2;

select u.preferences from cinema.users u where u.user_id = 2;

update cinema.users 
set preferences = preferences - 'autoplay'
where user_id = 1;

select u.preferences from cinema.users u where u.user_id = 1;

-- 4.5 разделить json документ на несколько строк по узлам
select 
    user_id,
    jsonb_object_keys(preferences) as preference_key,
    preferences->jsonb_object_keys(preferences) as preference_value
from cinema.users
where user_id in (1, 2);


select 
    u.user_id,
    u.full_name,
    'favorite_genre' as preference_type,
    jsonb_array_elements_text(u.preferences->'favorite_genres') as genre
from cinema.users u
where u.user_id in (1, 2)
order by u.user_id, genre;

-- развертывание всех preferences в плоскую структуру
with flattened_preferences as (
    select 
        user_id,
        key as preference_key,
        value as preference_value,
        'basic' as preference_type
    from cinema.users,
    lateral jsonb_each(preferences) as e(key, value)
    where jsonb_typeof(value) not in ('object', 'array')
        and user_id in (1, 2)
    
    union all
    
    select 
        u.user_id,
        'notifications.' || n.key as preference_key,
        n.value as preference_value,
        'notification' as preference_type
    from cinema.users u
    cross join lateral jsonb_each(u.preferences->'notifications') as n(key, value)
    where u.user_id in (1, 2)
    
    union all
    
    select 
        u.user_id,
        'favorite_genres' as preference_key,
        to_jsonb(jsonb_array_elements_text(u.preferences->'favorite_genres')) as preference_value,
        'genre' as preference_type
    from cinema.users u
    where u.user_id in (1, 2)
    
    union all
    
    select 
        u.user_id,
        'parental_control.' || pc.key as preference_key,
        pc.value as preference_value,
        'parental' as preference_type
    from cinema.users u
    cross join lateral jsonb_each(u.preferences->'parental_control') as pc(key, value)
    where u.preferences ? 'parental_control'
        and u.user_id in (1, 2)
)
select 
    user_id,
    preference_key,
    preference_value,
    preference_type
from flattened_preferences
order by user_id, preference_type, preference_key;
