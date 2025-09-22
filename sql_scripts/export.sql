set search_path to cinema;

copy users to '/tmp/users.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy movies to '/tmp/movies.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy devices to '/tmp/devices.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy payment_methods to '/tmp/payment_methods.csv' with (format csv, header true, delimiter ',', encoding 'utf8');

copy viewing_history to '/tmp/viewing_history.csv' with (format csv, header true, delimiter ',', encoding 'utf8');
