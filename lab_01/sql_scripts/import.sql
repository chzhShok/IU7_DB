set search_path to cinema;

begin;

copy users from '/tmp/users.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy movies from '/tmp/movies.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy devices from '/tmp/devices.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy payment_methods from '/tmp/payment_methods.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy viewing_history from '/tmp/viewing_history.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

commit;

select 
    (select count(*) from users) as users_count,
    (select count(*) from movies) as movies_count,
    (select count(*) from devices) as devices_count,
    (select count(*) from payment_methods) as payments_count,
    (select count(*) from viewing_history) as views_count;
