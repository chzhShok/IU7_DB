create extension if not exists plpython3u;

-- скалярная функция
-- проверка пароля
create or replace function check_password_strength(password text)
returns boolean
as $$
import re

if not password:
    return false

if len(password) < 8:
    return false

checks = [
    r'\d',
    r'[a-z]',
    r'[a-z]',
    r'[!@#$%^&*()_+\-=\[\]{};:\"\\|,.<>\/?]'
]

for pattern in checks:
    if not re.search(pattern, password):
        return false

return true
$$ language plpython3u;

select check_password_strength('strongpass123!');
select check_password_strength('1239aa!');

-- агрегатная функция
-- средний рейтинг режиссера
create or replace function filtered_avg_rating_accum(state numeric[], rating numeric)
returns numeric[]
as $$
if rating is not none:
    if state[0] is none:
        return [1, rating]
    else:
        return [state[0] + 1, state[1] + rating]
return state
$$ language plpython3u;

create or replace function filtered_avg_rating_final(state numeric[])
returns numeric
as $$
if state is none or state[0] is none or state[0] == 0:
    return none
return state[1] / state[0]
$$ language plpython3u;

create or replace aggregate filtered_avg_rating(numeric) (
    sfunc = filtered_avg_rating_accum,
    stype = numeric[],
    finalfunc = filtered_avg_rating_final,
    initcond = '{0,0}'
);

select director, filtered_avg_rating(imdb_rating) as avg_rating
from cinema.movies 
group by director;

-- табличная функция
-- активность пользователя по дням
create or replace function get_user_activity_periods(user_id integer)
returns table(period_date date, view_count bigint, total_duration interval, avg_completion numeric)
as $$
query = """
select 
    date(vh.start_time) as view_date,
    count(*) as view_count,
    sum(vh.end_time - vh.start_time) as total_duration,
    avg(vh.viewed_percentage) as avg_completion
from cinema.viewing_history vh
where vh.user_id = $1
group by date(vh.start_time)
order by view_date desc
"""

plan = plpy.prepare(query, ["integer"])
result = plpy.execute(plan, [user_id])

for row in result:
    yield (row["view_date"], row["view_count"], row["total_duration"], float(row["avg_completion"]) if row["avg_completion"] else 0)
$$ language plpython3u;

select * from get_user_activity_periods(1);

-- хранимая процедура
-- изменение подписки пользователя
create or replace function upgrade_user_subscription(
    target_user_id integer, 
    new_subscription_type varchar,
    out old_subscription varchar,
    out new_subscription varchar,
    out upgrade_date timestamp
)
as $$
current_sub_query = "select subscription_type from cinema.users where user_id = $1"
plan = plpy.prepare(current_sub_query, ["integer"])
current_result = plpy.execute(plan, [target_user_id])

if not current_result:
    plpy.error(f"user with id {target_user_id} not found")

old_sub = current_result[0]["subscription_type"]

valid_subscriptions = ['basic', 'standard', 'premium']
if new_subscription_type not in valid_subscriptions:
    plpy.error(f"invalid subscription type. must be one of: {valid_subscriptions}")

update_query = """
update cinema.users 
set subscription_type = $1 
where user_id = $2
returning subscription_type
"""

plan = plpy.prepare(update_query, ["varchar", "integer"])
update_result = plpy.execute(plan, [new_subscription_type, target_user_id])

return (old_sub, new_subscription_type, plpy.execute("select current_timestamp as now")[0]["now"])
$$ language plpython3u;

select * from upgrade_user_subscription(1, 'basic');

-- определяемый пользователем тип данных
-- дата и длительность просмотра
create or replace type viewing_time as (
    viewing_date date,
    viewing_duration interval
);

create or replace function viewing_time_to_string(vt viewing_time)
returns text
as $$
if vt is none:
    return "null"

date_part = vt.get('viewing_date')
duration_part = vt.get('viewing_duration')

return f"date: {date_part}, duration: {duration_part}"
$$ language plpython3u;

select create_viewing_time('2024-01-15'::date, '2 hours 30 minutes'::interval);
select viewing_time_to_string(('2024-01-15'::date, '2 hours 30 minutes'::interval));

-- триггер
-- обновление last_login_date при вставке
create or replace function update_device_login_trigger()
returns trigger
as $$
if td["new"] and td["new"]["device_id"]:
    device_id = td["new"]["device_id"]
    
    update_query = """
    update cinema.devices 
    set last_login_date = current_date 
    where device_id = $1
    """
    
    plan = plpy.prepare(update_query, ["integer"])
    plpy.execute(plan, [device_id])

return none
$$ language plpython3u;

create or replace trigger update_device_login_trigger
    after insert on cinema.viewing_history
    for each row
    execute function update_device_login_trigger();

insert into cinema.viewing_history (user_id, movie_id, device_id, start_time, end_time, viewed_percentage)
values (1, 1, 1, now(), now() + interval '2 hours', 95);

select * from cinema.devices where device_id = 1;
select * from cinema.viewing_history vh where vh.device_id = 1;
