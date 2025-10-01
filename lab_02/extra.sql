drop table if exists table1;
drop table if exists table2;

create table table1 (
	id integer,
	var1 text,
	valid_from_dttm date,
	valid_to_dttm date
);

create table table2 (
	id integer,
	var2 text,
	valid_from_dttm date,
	valid_to_dttm date
);

--insert into table1 (id, var1, valid_from_dttm, valid_to_dttm)
--values (1, 'a', '2018-09-01', '2018-09-15'),
--	   (1, 'b', '2018-09-16', '5999-12-31');

select * from table1;

--insert into table2 (id, var2, valid_from_dttm, valid_to_dttm)
--values (1, 'a', '2018-09-01', '2018-09-18'),
--	   (1, 'b', '2018-09-19', '5999-12-31');

select * from table2;

select 
    t1.id,
    t1.var1,
    t2.var2,
    greatest(t1.valid_from_dttm, t2.valid_from_dttm) as valid_from_dttm,
    least(t1.valid_to_dttm, t2.valid_to_dttm) as valid_to_dttm
from table1 t1
join table2 t2 on t1.id = t2.id
where greatest(t1.valid_from_dttm, t2.valid_from_dttm) <= 
      least(t1.valid_to_dttm, t2.valid_to_dttm)
order by t1.id, valid_from_dttm;
