set search_path to cinema;

-- таблица пользователей
alter table users add constraint pk_user_id primary key (user_id);

alter table users alter column email set not null;
alter table users alter column password_hash set not null;
alter table users alter column full_name set not null;
alter table users alter column registration_date set not null;
alter table users alter column subscription_type set not null;

alter table users alter column registration_date set default current_date;
alter table users alter column created_at set default current_timestamp;

alter table users add constraint unique_email unique (email);
alter table users add constraint email check (email like '%@%.%');
alter table users add constraint registration_date check (registration_date between '2020-01-01' and current_date);
alter table users add constraint subscription_type check (subscription_type in ('basic', 'standard', 'premium'));
alter table users add constraint created_at check (created_at <= current_timestamp);

-- таблица фильмов/сериалов
alter table movies add constraint pk_movie_id primary key (movie_id);

alter table movies alter column title set not null;
alter table movies alter column director set not null;

alter table movies alter column created_at set default current_timestamp;

alter table movies add constraint release_year check (release_year between 1900 and extract(year from current_date) + 5);
alter table movies add constraint duration_minutes check (duration_minutes > 0);
alter table movies add constraint imdb_rating check (imdb_rating between 0 and 10);
alter table movies add constraint created_at check (created_at <= current_timestamp);

-- таблица устройств
alter table devices add constraint pk_device_id primary key (device_id);
alter table devices add constraint fk_user_id foreign key (user_id) references users(user_id) on delete cascade;

alter table devices alter column user_id set not null;
alter table devices alter column device_type set not null;
alter table devices alter column device_name set not null;
alter table devices alter column app_version set not null;

alter table devices alter column is_active set default true;
alter table devices alter column created_at set default current_timestamp;

alter table devices add constraint device_type check (device_type in ('smarttv', 'phone', 'tablet', 'pc', 'console'));
alter table devices add constraint last_login_date check (last_login_date <= current_date);
alter table devices add constraint user_id check (created_at <= current_timestamp);

-- таблица способов оплаты
alter table payment_methods add constraint pk_payment_method_id primary key (payment_method_id);
alter table payment_methods add constraint fk_user_id foreign key (user_id) references users(user_id) on delete cascade;

alter table payment_methods alter column user_id set not null;
alter table payment_methods alter column method_type set not null;
alter table payment_methods alter column added_date set not null;

alter table payment_methods alter column is_default set default false;
alter table payment_methods alter column added_date set default current_date;
alter table payment_methods alter column created_at set default current_timestamp;

alter table payment_methods add constraint method_type check (method_type in ('credit card', 'debit card', 'paypal', 'google pay', 'apple pay'));
alter table payment_methods add constraint card_last_digits check (card_last_digits::varchar(4) ~ '^[0-9]{4}$');
alter table payment_methods add constraint added_date check (added_date <= current_timestamp);
alter table payment_methods add constraint expiry_date check (expiry_date > added_date);
alter table payment_methods add constraint created_at check (created_at <= current_timestamp);

-- таблица-связка истории просмотров
alter table viewing_history add constraint pk_view_id primary key (view_id);
alter table viewing_history add constraint fk_user_id foreign key (user_id) references users(user_id) on delete cascade;
alter table viewing_history add constraint fk_movie_id foreign key (movie_id) references movies(movie_id) on delete cascade;
alter table viewing_history add constraint fk_device_id foreign key (device_id) references devices(device_id) on delete cascade;

alter table viewing_history alter column user_id set not null;
alter table viewing_history alter column movie_id set not null;
alter table viewing_history alter column device_id set not null;
alter table viewing_history alter column start_time set not null;
alter table viewing_history alter column viewed_percentage set not null;

alter table viewing_history alter column start_time set default current_timestamp;
alter table viewing_history alter column created_at set default current_timestamp;

alter table viewing_history add constraint start_time check (start_time <= current_timestamp);
alter table viewing_history add constraint end_time check (end_time >= start_time);
alter table viewing_history add constraint viewed_percentage check (viewed_percentage between 0 and 100);
alter table viewing_history add constraint created_at check (created_at <= current_timestamp);
