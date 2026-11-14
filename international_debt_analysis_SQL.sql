create database international_debt_final;
use international_debt_final;
show tables;

select count(*) as total_countries
from countries;

select count(*) as total_indicators
from indicators;

select count(*) as total_debt_records
from debt_data;

select count(*) as total_footnotes
from footnotes;

select count(*) as total_country_series
from country_series;

alter table countries
modify column `Code` varchar(3) not null;

alter table countries
add primary key (`Code`);

alter table indicators
modify column `Code` varchar(100) not null;

alter table indicators
add primary key (`Code`);

alter table debt_data
modify column `Country Code` varchar(3);

alter table footnotes
modify column `Country Code` varchar(3);

alter table country_series
modify column `Country Code` varchar(3);

alter table debt_data
modify column `Series Code` varchar(100);

alter table footnotes
modify column `Series Code` varchar(100);

alter table country_series
modify column `Series Code` varchar(100);

alter table debt_data
add foreign key (`Country Code`)
references countries(`Code`);

alter table debt_data
add foreign key (`Series Code`)
references indicators(`Code`);

alter table footnotes
add foreign key (`Country Code`)
references countries(`Code`);

alter table footnotes
modify column `Series Code` varchar(100);

alter table footnotes
add foreign key (`Series Code`)
references indicators(`Code`);

alter table country_series
add foreign key (`Country Code`)
references countries(`Code`);

alter table country_series
add foreign key (`Series Code`)
references indicators(`Code`);

select
    table_name,
    column_name,
    referenced_table_name,
    referenced_column_name
from information_schema.key_column_usage
where table_schema = 'international_debt_final'
and referenced_table_name is not null
order by table_name, column_name;


use international_debt_db;

select *
from debt_data
limit 10;

select count(*) as total_countries
from countries
where `Region` <> 'Unknown';

select count(*) as total_indicators
from indicators;

select count(*) as total_records
from debt_data;

select min(`Year`) as first_year,
       max(`Year`) as last_year
from debt_data;

select distinct `Region`
from countries
where `Region` <> 'Unknown'
order by `Region`;

select distinct `Income Group`
from countries
order by `Income Group`;

select `Country Name`, `Series Name`, `Year`, `Value`
from debt_data
where `Country Code` = 'IND'
and `Year` = 2024
limit 20;

select count(distinct `Series Code`) as used_indicators
from debt_data;

select `Year`, count(*) as total_records
from debt_data
group by `Year`
order by `Year`;

select c.`Short Name` as Country,
       c.`Region` as Region
from countries c
where c.`Region` <> 'Unknown'
order by Country;

select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
order by Debt_Billion_USD desc;

select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
order by Debt_Billion_USD desc
limit 10;

select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
and d.`Value` > 0
order by Debt_Billion_USD
limit 10;

select c.`Region`,
       round(sum(d.`Value`) / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
group by c.`Region`
order by Debt_Billion_USD desc;

select c.`Region`,
       round(avg(d.`Value`) / 1000000000, 2) as Average_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
group by c.`Region`
order by Average_Billion_USD desc;

select `Region`, count(*) as total_countries
from countries
where `Region` <> 'Unknown'
group by `Region`
order by total_countries desc;

select `Year`,
       round(`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data
where `Country Code` = 'IND'
and `Series Code` = 'DT.DOD.DECT.CD'
order by `Year`;

select `Series Name`,
       round(`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data
where `Country Code` = 'IND'
and `Year` = 2024
and `Series Code` in (
    'DT.DOD.DECT.CD',
    'DT.DOD.DLXF.CD',
    'DT.DOD.DSTC.CD'
);

select c.`Region`,
       round(sum(d.`Value`) / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
group by c.`Region`
having sum(d.`Value`) > 1000000000000
order by Debt_Billion_USD desc;


select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD,
       rank() over (order by d.`Value` desc) as Debt_Rank
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
order by Debt_Rank;

select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD,
       case
           when d.`Value` >= 1000000000000 then 'High'
           when d.`Value` >= 100000000000 then 'Medium'
           else 'Low'
       end as Debt_Category
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
order by d.`Value` desc;

select d.`Country Name` as Country,
       round(d.`Value` / 1000000000, 2) as Debt_Billion_USD
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
and d.`Value` > (
    select avg(d2.`Value`)
    from debt_data d2
    join countries c2
    on d2.`Country Code` = c2.`Code`
    where d2.`Year` = 2024
    and d2.`Series Code` = 'DT.DOD.DECT.CD'
    and c2.`Region` <> 'Unknown'
)
order by d.`Value` desc;

select d.`Country Name` as Country,
       round(
           100 * d.`Value` / nullif(sum(d.`Value`) over (), 0),
           2
       ) as Debt_Share_Percent
from debt_data d
join countries c
on d.`Country Code` = c.`Code`
where d.`Year` = 2024
and d.`Series Code` = 'DT.DOD.DECT.CD'
and c.`Region` <> 'Unknown'
order by Debt_Share_Percent desc;

select `Country Name` as Country,
       `Year`,
       round(`Value` / 1000000000, 2) as Debt_Billion_USD,
       round(
           lag(`Value`) over (
               partition by `Country Code`
               order by `Year`
           ) / 1000000000, 2
       ) as Previous_Year_Billion
from debt_data
where `Country Code` = 'IND'
and `Series Code` = 'DT.DOD.DECT.CD'
order by `Year`;

with yearly_debt as (
    select `Year`, `Value`,
           lag(`Value`) over (order by `Year`) as Previous_Value
    from debt_data
    where `Country Code` = 'IND'
    and `Series Code` = 'DT.DOD.DECT.CD'
)
select `Year`,
       round((`Value` - Previous_Value) / 1000000000, 2)
           as Change_Billion_USD
from yearly_debt
order by `Year`;

with regional_debt as (
    select c.`Region`,
           sum(d.`Value`) as Total_Debt
    from debt_data d
    join countries c
    on d.`Country Code` = c.`Code`
    where d.`Year` = 2024
    and d.`Series Code` = 'DT.DOD.DECT.CD'
    and c.`Region` <> 'Unknown'
    group by c.`Region`
)
select `Region`,
       round(Total_Debt / 1000000000, 2) as Debt_Billion_USD,
       dense_rank() over (order by Total_Debt desc) as Region_Rank
from regional_debt;

with ranked_countries as (
    select d.`Country Name` as Country,
           c.`Region`,
           d.`Value`,
           row_number() over (
               partition by c.`Region`
               order by d.`Value` desc
           ) as Position
    from debt_data d
    join countries c
    on d.`Country Code` = c.`Code`
    where d.`Year` = 2024
    and d.`Series Code` = 'DT.DOD.DECT.CD'
    and c.`Region` <> 'Unknown'
)
select `Region`, Country,
       round(`Value` / 1000000000, 2) as Debt_Billion_USD
from ranked_countries
where Position = 1
order by Debt_Billion_USD desc;

-- Q29. Find the top 3 debt countries in each region
with ranked_countries as (
    select d.`Country Name` as Country,
           c.`Region`,
           d.`Value`,
           dense_rank() over (
               partition by c.`Region`
               order by d.`Value` desc
           ) as Debt_Rank
    from debt_data d
    join countries c
    on d.`Country Code` = c.`Code`
    where d.`Year` = 2024
    and d.`Series Code` = 'DT.DOD.DECT.CD'
    and c.`Region` <> 'Unknown'
)
select `Region`, Country,
       round(`Value` / 1000000000, 2) as Debt_Billion_USD,
       Debt_Rank
from ranked_countries
where Debt_Rank <= 3
order by `Region`, Debt_Rank;

with country_shares as (
    select d.`Country Name` as Country,
           round(
               100 * d.`Value` / nullif(sum(d.`Value`) over (), 0),
               2
           ) as Share_Percent
    from debt_data d
    join countries c
    on d.`Country Code` = c.`Code`
    where d.`Year` = 2024
    and d.`Series Code` = 'DT.DOD.DECT.CD'
    and c.`Region` <> 'Unknown'
)
select *
from country_shares
where Share_Percent > 5
order by Share_Percent desc;