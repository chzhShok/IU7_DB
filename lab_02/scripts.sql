-- 1. инструкция select, использующая предикат сравнения
-- пользователи с премиум подпиской, зарегистрированные после 2023 года

select user_id, full_name, email, registration_date, subscription_type
from cinema.users
where subscription_type = 'premium' 
and registration_date > '2023-01-01'
order by registration_date desc;

-- 2. инструкция select, использующая предикат between
-- фильмы, выпущенные между 2010 и 2020 годами с рейтингом больше или равно 7

select movie_id, title, director, release_year, genres, imdb_rating
from cinema.movies
where release_year between 2010 and 2020
and imdb_rating >= 7.0
order by release_year desc, imdb_rating desc;

-- 3. инструкция select, использующая предикат like
-- пользователи с gmail почтой

select user_id, full_name, email, registration_date
from cinema.users
where email like '%@gmail.com'
order by full_name;

-- 4. инструкция select, использующая предикат in с вложенным подзапросом
-- cпособы оплаты для пользователей с базовой подпиской

select pm.payment_method_id, u.full_name, pm.method_type, pm.card_last_digits
from cinema.payment_methods pm
join cinema.users u on pm.user_id = u.user_id
where pm.user_id in (
    select user_id
    from cinema.users
    where subscription_type = 'basic'
)
order by u.full_name;

-- 5. инструкция select, использующая предикат exists с вложенным подзапросом
-- пользователи, у которых зарегистрировано хотя бы одно активное устройство

select user_id, full_name, email, subscription_type
from cinema.users u
where exists (
    select 1
    from cinema.devices d
    where d.user_id = u.user_id
    and d.is_active = true
)
order by full_name;

-- 6. инструкция select, использующая предикат сравнения с квантором
-- фильмы, у которых рейтинг выше всех фильмов бодайна

select movie_id, title, director, imdb_rating, release_year
from cinema.movies m1
where imdb_rating > all (
    select imdb_rating
    from cinema.movies m2
    where m2.director like '%beaudine%'
)
order by imdb_rating desc;

-- 7. инструкция select, использующая агрегатные функции в выражениях столбцов
-- анализ пользователей по типам подписок

select 
    subscription_type,
    count(user_id) as user_count,
    round(count(user_id) * 100.0 / (select count(*) from cinema.users), 2) as percentage,
    avg(extract(year from age(current_date, registration_date))) as avg_years_registered,
    min(registration_date) as earliest_registration,
    max(registration_date) as latest_registration
from cinema.users
group by subscription_type
order by user_count desc;

-- 8. инструкция select, использующая скалярные подзапросы в выражениях столбцов
-- информация о пользователях с количеством их устройств и просмотров

select 
    user_id,
    full_name,
    email,
    subscription_type,
    registration_date,
    (select count(*) from cinema.devices d where d.user_id = u.user_id) as devices_count,
    (select count(*) from cinema.viewing_history vh where vh.user_id = u.user_id) as total_views,
    (select max(start_time) from cinema.viewing_history vh where vh.user_id = u.user_id) as last_watch_date
from cinema.users u
where subscription_type = 'premium'
order by full_name;

-- 9. инструкция select, использующая простое выражение case
-- группировка способов оплаты по типам

select 
    u.full_name,
    pm.method_type,
    case pm.method_type
        when 'credit card' then 'bank card'
        when 'debit card' then 'bank card'
        when 'paypal' then 'e-wallet'
        when 'google pay' then 'mobile payment'
        when 'apple pay' then 'mobile payment'
        else 'other payment'
    end as payment_category,
    pm.card_last_digits,
    pm.is_default
from cinema.payment_methods pm
join cinema.users u on pm.user_id = u.user_id
order by u.full_name, pm.is_default desc;

-- 10. инструкция select, использующая поисковое выражение case
-- группировка фильмов по качеству на основе рейтинга

select 
    title,
    director,
    imdb_rating,
    case
        when imdb_rating >= 9.0 then 'masterpiece'
        when imdb_rating >= 8.0 then 'excellent'
        when imdb_rating >= 7.0 then 'very good'
        when imdb_rating >= 6.0 then 'good'
        when imdb_rating >= 5.0 then 'average'
        else 'below average'
    end as quality_category,
    release_year
from cinema.movies
where imdb_rating > 0
order by imdb_rating desc;

-- 11. создание новой временной локальной таблицы из результирующего набора данных инструкции select
-- таблица фильмов с количеством просмотров и средним процентом завершения

select 
    m.movie_id,
    m.title,
    m.director,
    m.imdb_rating,
    count(vh.view_id) as total_views,
    round(avg(vh.viewed_percentage), 2) as avg_completion_rate
into temp table popular_movies
from cinema.movies m
left join cinema.viewing_history vh on m.movie_id = vh.movie_id
where m.imdb_rating > 7.0
group by m.movie_id, m.title, m.director
having count(vh.view_id) > 0
order by total_views desc;

select * from popular_movies;

-- 12. инструкция select, использующая вложенные коррелированные подзапросы в качестве производных таблиц в предложении from
-- самые популярные фильмы по разным критериям

select 'by view count' as criteria, title as "best movie", director
from cinema.movies m 
join (
    select movie_id, count(view_id) as total_views
    from cinema.viewing_history
    group by movie_id
    order by total_views desc
    limit 1
) as vc on vc.movie_id = m.movie_id

union

select 'by completion rate' as criteria, title as "best movie", director
from cinema.movies m 
join (
    select movie_id, avg(viewed_percentage) as avg_completion
    from cinema.viewing_history
    group by movie_id
    having count(view_id) >= 5
    order by avg_completion desc
    limit 1
) as cr on cr.movie_id = m.movie_id;

-- 13. инструкция select, использующая вложенные подзапросы с уровнем вложенности 3
-- самые активные пользователи

select 'most active user' as criteria, full_name as "user name"
from cinema.users
where user_id in (
    select user_id
    from cinema.viewing_history
    group by user_id
    having count(view_id) = (
        select max(view_count)
        from (
            select count(view_id) as view_count
            from cinema.viewing_history
            group by user_id
        ) as user_views
    )
);

-- 14. инструкция select, консолидирующая данные с помощью предложения group by, но без предложения having
-- для каждого устройства информация об активности

select 
    d.device_id,
    d.device_name,
    d.device_type,
    u.full_name as user_name,
    d.app_version,
    d.last_login_date,
    count(vh.view_id) as total_views,
    round(avg(vh.viewed_percentage), 2) as avg_completion
from cinema.devices d
join cinema.users u 
on d.user_id = u.user_id
left join cinema.viewing_history vh on d.device_id = vh.device_id
group by d.device_id, d.device_name, d.device_type, u.full_name, d.app_version, d.last_login_date
order by total_views desc;

-- 15. инструкция select, консолидирующая данные с помощью предложения group by и предложения having
-- режиссеры, у которых средний рейтинг фильмов выше общего среднего

select 
    director,
    count(movie_id) as total_movies,
    avg(imdb_rating) as avg_director_rating,
    avg(duration_minutes) as avg_duration
from cinema.movies
group by director
having avg(imdb_rating) > (
    select avg(imdb_rating) 
    from cinema.movies 
)
and count(movie_id) >= 2
order by avg_director_rating desc;

-- 16. одно строчная инструкция insert, выполняющая вставку в таблицу одной строки значений
-- добавление нового фильма

insert into cinema.movies (title, director, release_year, genres, duration_minutes, imdb_rating, created_at)
values ('interstellar', 'christopher nolan', 2014, 'action, sci-fi, drama', 169, 8.7, default);

-- 17. многострочная инструкция insert, выполняющая вставку в таблицу результирующего набора данных вложенного подзапроса
-- добавление кредитной карты как способа оплаты для пользователей с более чем 10 просмотрами

insert into cinema.payment_methods (user_id, method_type, card_last_digits, is_default, added_date, expiry_date, created_at)
select 
    user_id,
    'credit card',
    9999,
    false,
    current_date,
    current_date + interval '2 years',
    current_timestamp
from cinema.users
where user_id in (
    select user_id 
    from cinema.viewing_history 
    group by user_id 
    having count(view_id) > 10
);

-- 18. простая инструкция update
-- повышение подписки пользователя до премиум

update cinema.users
set subscription_type = 'premium'
where user_id = 1;

-- 19. инструкция update со скалярным подзапросом в предложении set
-- установка процента просмотра равным среднему проценту пользователя

update cinema.viewing_history
set viewed_percentage = (
    select avg(viewed_percentage)
    from cinema.viewing_history
    where user_id = 1
)
where view_id = 1 and user_id = 1;

-- 20. простая инструкция delete
-- удаление фильмов с нулевым или отсутствующим рейтингом

delete from cinema.movies
where imdb_rating = 0 or imdb_rating is null;

-- 21. инструкция delete с вложенным коррелированным подзапросом в предложении where
-- удаление пользователей, у которых нет активных устройств

delete from cinema.users
where user_id in (
    select u.user_id
    from cinema.users u
    left join cinema.devices d on u.user_id = d.user_id and d.is_active = true
    where d.device_id is null
);

-- 22. инструкция select, использующая простое обобщенное табличное выражение
-- cte user_viewing_stats, который для каждого пользователя считает статистику

with user_viewing_stats (userid, totalviews, avgviewpercentage) as (
    select 
        user_id, 
        count(*) as totalviews,
        avg(viewed_percentage) as avgviewpercentage
    from cinema.viewing_history
    group by user_id
)
select 
    avg(totalviews) as "среднее количество просмотров на пользователя",
    avg(avgviewpercentage) as "средний процент просмотра"
from user_viewing_stats;

-- 23. инструкция select, использующая рекурсивное обобщенное табличное выражение
-- для каждого пользователя цепочка из до 3 последовательных просмотров

with recursive viewing_chain (view_id, user_id, movie_id, start_time, chain_length, root_movie) as
(
    select 
        view_id,
        user_id,
        movie_id,
        start_time,
        1 as chain_length,
        movie_id as root_movie
    from cinema.viewing_history 
    where view_id in (
        select min(view_id) 
        from cinema.viewing_history 
        group by user_id
    )
    
    union all
    
    select 
        vh.view_id,
        vh.user_id,
        vh.movie_id,
        vh.start_time,
        vc.chain_length + 1,
        vc.root_movie
    from cinema.viewing_history vh
    inner join viewing_chain vc on vh.user_id = vc.user_id
    where vh.start_time > vc.start_time
      and vh.view_id = (
          select min(view_id) 
          from cinema.viewing_history 
          where user_id = vc.user_id 
            and start_time > vc.start_time
      )
      and vc.chain_length < 3
)

select 
    u.full_name as "пользователь",
    m.title as "фильм",
    vc.start_time as "время начала",
    vc.chain_length as "порядковый номер в цепочке",
    (select title from cinema.movies where movie_id = vc.root_movie) as "первый фильм в цепочке"
from viewing_chain vc
join cinema.users u on vc.user_id = u.user_id
join cinema.movies m on vc.movie_id = m.movie_id
order by u.full_name, vc.start_time;

-- 24. оконные функции. использование конструкций min/max/avg over()
-- статиситика по пользователям

select distinct
    u.user_id,
    u.full_name as "пользователь",
    u.email as "email",
    u.subscription_type as "тип подписки",
    u.registration_date as "дата регистрации",
    count(vh.view_id) over(partition by u.user_id) as "всего просмотров",
    avg(vh.viewed_percentage) over(partition by u.user_id) as "средний процент просмотра",
    min(vh.viewed_percentage) over(partition by u.user_id) as "минимальный процент просмотра",
    max(vh.viewed_percentage) over(partition by u.user_id) as "максимальный процент просмотра",
    count(d.device_id) over(partition by u.user_id) as "количество устройств",
    count(pm.payment_method_id) over(partition by u.user_id) as "количество способов оплаты"
from cinema.users u
left join cinema.viewing_history vh on u.user_id = vh.user_id
left join cinema.devices d on u.user_id = d.user_id and d.is_active = true
left join cinema.payment_methods pm on u.user_id = pm.user_id
order by u.user_id;

-- 25. оконные функции для устранения дублей
-- устранение дублей по просмотрам

with viewing_with_duplicates as (
    select vh.* from cinema.viewing_history vh
    union all
    select vh.* from cinema.viewing_history vh
    where vh.view_id in (select view_id from cinema.viewing_history order by view_id limit 10)
),
numbered_viewings as (
    select 
        *,
        row_number() over(
            partition by user_id, movie_id, start_time, device_id
            order by view_id
        ) as duplicate_num
    from viewing_with_duplicates
)

select 
    view_id,
    user_id,
    movie_id,
    device_id,
    start_time,
    end_time,
    viewed_percentage,
    created_at
from numbered_viewings
where duplicate_num = 1
order by view_id;
