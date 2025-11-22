CREATE TABLE cinema.load_log (
    log_id serial PRIMARY KEY,
    file_name text,
    table_name text,
    record_count int,
    load_status text,
    error_message text,
    load_timestamp timestamp default current_timestamp
);
