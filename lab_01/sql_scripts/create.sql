drop schema if exists cinema cascade;
create schema cinema;

SET search_path TO cinema;

-- таблица пользователей
create table cinema.users (
    user_id serial,
    email text,
    password_hash varchar(255),
    full_name text,
    registration_date date,
    subscription_type varchar(20),
    created_at timestamp
);

-- таблица фильмов/сериалов
create table cinema.movies (
    movie_id serial,
    title varchar(255),
    director text,
    release_year integer,
    genres text,
    duration_minutes integer,
    imdb_rating decimal(2,1),
    created_at timestamp
);

-- таблица устройств
create table cinema.devices (
    device_id serial,
    user_id integer,
    device_type varchar(20),
    device_name varchar(255),
    last_login_date date,
    app_version varchar(20),
    is_active boolean,
    created_at timestamp
);

-- таблица способов оплаты
create table cinema.payment_methods (
    payment_method_id serial,
    user_id integer,
    method_type varchar(20),
    card_last_digits decimal(4,0),
    is_default boolean,
    added_date date,
    expiry_date date,
    created_at timestamp
);

-- таблица-связка истории просмотров
create table cinema.viewing_history (
    view_id serial,
    user_id integer,
    movie_id integer,
    device_id integer,
    start_time timestamp,
    end_time timestamp,
    viewed_percentage integer,
    created_at timestamp
);
