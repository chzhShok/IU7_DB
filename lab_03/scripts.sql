-- скалярная функция
-- средний рейтинг фильмов режиссера
CREATE OR REPLACE FUNCTION get_director_avg_rating(director_name TEXT)
RETURNS DECIMAL AS $$
DECLARE
    avg_rating DECIMAL;
BEGIN
    SELECT AVG(imdb_rating) INTO avg_rating
    FROM cinema.movies 
    WHERE director = director_name;
    
    RETURN COALESCE(avg_rating, 0);
END;
$$ LANGUAGE plpgsql;

SELECT 
    director,
    get_director_avg_rating(director) as avg_rating
FROM cinema.movies 
GROUP BY director;

-- подставляемая табличная функция
-- пользователи по типу подписки
CREATE OR REPLACE FUNCTION get_users_by_subscription(sub_type TEXT)
RETURNS TABLE (
    user_id INT,
    email TEXT,
    full_name TEXT,
    registration_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.user_id, u.email, u.full_name, u.registration_date
    FROM cinema.users u
    WHERE u.subscription_type = sub_type
    ORDER BY u.registration_date DESC;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_users_by_subscription('premium');

-- многооператорная табличная функция
CREATE OR REPLACE FUNCTION get_user_viewing_stats()
RETURNS TABLE (
    user_id INT,
    full_name TEXT,
    total_views BIGINT,
    total_watch_time INTERVAL,
    favorite_device TEXT
) AS $$
DECLARE
    user_record RECORD;
    fav_device TEXT;
BEGIN
    CREATE TEMP TABLE temp_stats AS
    SELECT 
        u.user_id,
        u.full_name,
        COUNT(vh.view_id) as total_views,
        SUM(vh.end_time - vh.start_time) as total_watch_time,
        NULL::TEXT as favorite_device
    FROM cinema.users u
    LEFT JOIN cinema.viewing_history vh ON u.user_id = vh.user_id
    GROUP BY u.user_id, u.full_name;
    
    FOR user_record IN SELECT * FROM temp_stats 
    LOOP
        SELECT d.device_name INTO fav_device
        FROM cinema.devices d
        JOIN cinema.viewing_history vh ON d.device_id = vh.device_id
        WHERE vh.user_id = user_record.user_id
        GROUP BY d.device_id, d.device_name
        ORDER BY COUNT(*) DESC
        LIMIT 1;
        
        UPDATE temp_stats 
        SET favorite_device = COALESCE(fav_device, 'No views')
        WHERE temp_stats.user_id = user_record.user_id;
    END LOOP;
    
    RETURN QUERY SELECT * FROM temp_stats;
    
    DROP TABLE temp_stats;
END;
$$ LANGUAGE plpgsql;

select * from get_user_viewing_stats();

-- рекурсивная функция или функция с рекурсивным ОТВ
-- рекурсивная система рекомендаций фильмов на основе режиссеров
CREATE OR REPLACE FUNCTION get_movie_recommendations(start_movie_id INT, depth INT DEFAULT 3)
RETURNS TABLE (
    movie_id INT,
    title VARCHAR(255),
    director TEXT,
    level INT,
    path TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE movie_recursive AS (
        SELECT 
            m.movie_id,
            m.title,
            m.director,
            0 as level,
            m.title::TEXT as path
        FROM cinema.movies m
        WHERE m.movie_id = start_movie_id
        
        UNION ALL
        
        SELECT 
            m.movie_id,
            m.title,
            m.director,
            mr.level + 1,
            mr.path || ' -> ' || m.title
        FROM cinema.movies m
        INNER JOIN movie_recursive mr ON m.director = mr.director
        WHERE mr.level < depth 
          AND m.movie_id != mr.movie_id
          AND NOT (m.title = ANY(string_to_array(mr.path, ' -> ')))
    )

    SELECT * FROM movie_recursive;
END;
$$ LANGUAGE plpgsql;

select * from get_movie_recommendations(
(
	select movie_id 
	from cinema.movies
	where director = (
		select director
		from cinema.movies
		group by director
		order by count(*) desc
		limit 1
	)
	order by movie_id
	limit 1
)
);

-- хранимая процедура без параметров или с параметрами
-- обновление типа подписки пользователя
CREATE OR REPLACE PROCEDURE update_user_subscription(
    p_user_id INT,
    p_new_subscription TEXT
) AS $$
BEGIN
    IF p_new_subscription NOT IN ('basic', 'standard', 'premium') THEN
        RAISE EXCEPTION 'Invalid subscription type: %', p_new_subscription;
    END IF;
    
    UPDATE cinema.users 
    SET subscription_type = p_new_subscription
    WHERE user_id = p_user_id;
    
    RAISE NOTICE 'Subscription updated for user % to %', p_user_id, p_new_subscription;
    
    COMMIT;
END;
$$ LANGUAGE plpgsql;

call update_user_subscription(1, 'basic');

call update_user_subscription(1, 'aaa');

-- рекурсивная хранимая процедура или хранимая процедура с рекурсивным ОТВ
-- статистика по месяцам для определенных пользователей
CREATE OR REPLACE PROCEDURE generate_monthly_stats(p_year INT) AS $$
DECLARE
    month_record RECORD;
BEGIN
    CREATE TEMP TABLE monthly_stats (
        month_num INT,
        month_name TEXT,
        new_users BIGINT,
        total_views BIGINT
    );
    
    WITH RECURSIVE months AS (
        SELECT 1 as month_num, 'January' as month_name
        
        UNION ALL
        
        SELECT month_num + 1, 
               CASE month_num + 1
                   WHEN 2 THEN 'February'
                   WHEN 3 THEN 'March'
                   WHEN 4 THEN 'April'
                   WHEN 5 THEN 'May'
                   WHEN 6 THEN 'June'
                   WHEN 7 THEN 'July'
                   WHEN 8 THEN 'August'
                   WHEN 9 THEN 'September'
                   WHEN 10 THEN 'October'
                   WHEN 11 THEN 'November'
                   WHEN 12 THEN 'December'
               END
        FROM months
        WHERE month_num < 12
    )
    INSERT INTO monthly_stats
    SELECT 
        m.month_num,
        m.month_name,
        COUNT(DISTINCT u.user_id) as new_users,
        COUNT(vh.view_id) as total_views
    FROM months m
    LEFT JOIN cinema.users u ON EXTRACT(MONTH FROM u.registration_date) = m.month_num 
                             AND EXTRACT(YEAR FROM u.registration_date) = p_year
    LEFT JOIN cinema.viewing_history vh ON EXTRACT(MONTH FROM vh.start_time) = m.month_num 
                                        AND EXTRACT(YEAR FROM vh.start_time) = p_year
    GROUP BY m.month_num, m.month_name
    ORDER BY m.month_num;
    
    RAISE NOTICE 'Monthly statistics for year %:', p_year;
    FOR month_record IN SELECT * FROM monthly_stats ORDER BY month_num
    LOOP
        RAISE NOTICE 'Month % (%): New Users: %, Total Views: %', 
            month_record.month_num, 
            month_record.month_name,
            month_record.new_users,
            month_record.total_views;
    END LOOP;
    
    DROP TABLE monthly_stats;
END;
$$ LANGUAGE plpgsql;

call generate_monthly_stats(2024);

-- хранимая процедура с курсором
-- архивация истории просмотров за период
CREATE OR REPLACE PROCEDURE archive_viewing_history_by_range(
    p_start_date TIMESTAMP,
    p_end_date TIMESTAMP
) AS $$
DECLARE
    view_cursor CURSOR FOR
        SELECT view_id, user_id, movie_id, device_id, start_time, end_time
        FROM cinema.viewing_history
        WHERE start_time >= p_start_date 
          AND start_time < p_end_date;
    
    view_record RECORD;
    archived_count INT := 0;
BEGIN
    IF p_start_date >= p_end_date THEN
        RAISE EXCEPTION 'Start date (%) must be earlier than end date (%)', p_start_date, p_end_date;
    END IF;

    RAISE NOTICE 'Archiving records from % to %', p_start_date, p_end_date;

    CREATE TABLE IF NOT EXISTS cinema.viewing_history_archive (
        archive_id SERIAL PRIMARY KEY,
        view_id INT,
        user_id INT,
        movie_id INT,
        device_id INT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    OPEN view_cursor;
    
    LOOP
        FETCH view_cursor INTO view_record;
        EXIT WHEN NOT FOUND;
        
        INSERT INTO cinema.viewing_history_archive 
            (view_id, user_id, movie_id, device_id, start_time, end_time)
        VALUES 
            (view_record.view_id, view_record.user_id, view_record.movie_id, 
             view_record.device_id, view_record.start_time, view_record.end_time);
        
        DELETE FROM cinema.viewing_history WHERE view_id = view_record.view_id;
        
        archived_count := archived_count + 1;
    END LOOP;
    
    CLOSE view_cursor;

    RAISE NOTICE 'Archived % viewing history records from % to %', 
        archived_count, p_start_date, p_end_date;
END;
$$ LANGUAGE plpgsql;

call archive_viewing_history_by_range('2024-04-01 00:00:00', '2024-05-01 00:00:00');

select count(*) from cinema.viewing_history_archive ;

select count(*) from cinema.viewing_history vh where vh.start_time >= '2024-04-01 00:00:00' and vh.end_time <= '2024-05-01 00:00:00';

-- хранимая процедура доступа к метаданным
-- информация о колонках всех таблиц в схеме cinema
CREATE OR REPLACE PROCEDURE get_schema_metadata() AS $$
DECLARE
    table_record RECORD;
    column_record RECORD;
BEGIN
    RAISE NOTICE 'Database Schema Metadata for cinema:';
    RAISE NOTICE '=====================================';
    
    FOR table_record IN 
        SELECT 
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema = 'cinema'
        ORDER BY table_name
    LOOP
        RAISE NOTICE 'Table: % (%)', table_record.table_name, table_record.table_type;
        
        FOR column_record IN
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'cinema' 
              AND table_name = table_record.table_name
            ORDER BY ordinal_position
        LOOP
            RAISE NOTICE '  Column: % (Type: %, Nullable: %, Default: %)',
                column_record.column_name,
                column_record.data_type,
                column_record.is_nullable,
                COALESCE(column_record.column_default, 'NULL');
        END LOOP;
        RAISE NOTICE '';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

call get_schema_metadata();

-- триггер AFTER
-- логирование изменение подписки пользователя
CREATE TABLE IF NOT EXISTS cinema.subscription_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    old_subscription TEXT,
    new_subscription TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT DEFAULT CURRENT_USER
);

CREATE OR REPLACE FUNCTION log_subscription_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.subscription_type != NEW.subscription_type THEN
        INSERT INTO cinema.subscription_log 
            (user_id, old_subscription, new_subscription)
        VALUES 
            (NEW.user_id, OLD.subscription_type, NEW.subscription_type);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_subscription_change
    AFTER UPDATE ON cinema.users
    FOR EACH ROW
    EXECUTE FUNCTION log_subscription_change();

select u.subscription_type 
from cinema.users u 
where u.user_id = 1;

update cinema.users u set subscription_type = 'basic' where u.user_id = 1;

select * from cinema.subscription_log;

-- триггер INSTEAD OF
-- замена вставки по вью
CREATE OR REPLACE VIEW cinema.users_summary AS
SELECT 
    u.user_id,
    u.email,
    u.full_name,
    u.subscription_type,
    u.registration_date,
    COUNT(DISTINCT d.device_id) as device_count,
    COUNT(DISTINCT vh.view_id) as total_views
FROM cinema.users u
LEFT JOIN cinema.devices d ON u.user_id = d.user_id
LEFT JOIN cinema.viewing_history vh ON u.user_id = vh.user_id
GROUP BY u.user_id, u.email, u.full_name, u.subscription_type, u.registration_date;

CREATE OR REPLACE FUNCTION instead_of_insert_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cinema.users 
        (user_id, email, password_hash, full_name, registration_date, subscription_type, created_at)
    VALUES (
		(select max(user_id) + 1 from cinema.users),
        NEW.email,
        'temp_password_hash',
        NEW.full_name,
        COALESCE(NEW.registration_date, CURRENT_DATE),
        COALESCE(NEW.subscription_type, 'basic'),
        CURRENT_TIMESTAMP
    )
    RETURNING user_id INTO NEW.user_id;
    
    NEW.device_count := 0;
    NEW.total_views := 0;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE or replace TRIGGER instead_of_insert_user_trigger
    INSTEAD OF INSERT ON cinema.users_summary
    FOR EACH ROW
    EXECUTE FUNCTION instead_of_insert_user();


INSERT INTO cinema.users_summary (email, full_name) VALUES ('cool@minion.com', 'bla bla');

select * from cinema.users_summary
where email = 'cool@minion.com';

select * from cinema.users u 
where email = 'cool@minion.com';
