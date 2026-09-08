-- Grain: one row per calendar month and plan_code.
-- The month spine comes from dim_date, so the reporting window follows the data.
with months as (
  select distinct calendar_month from {{ ref('dim_date') }}
), base as (
  select m.calendar_month, s.plan_code,
    count(*) filter (where s.start_date <= last_day(m.calendar_month) and (s.cancelled_at is null or s.cancelled_at > last_day(m.calendar_month))) active_subscribers,
    count(*) filter (where date_trunc('month', s.cancelled_at) = m.calendar_month) churned_subscribers
  from months m cross join {{ ref('stg_subscriptions') }} s group by 1,2
)
select *, case when lag(active_subscribers) over(partition by plan_code order by calendar_month) > 0
  then churned_subscribers::double / lag(active_subscribers) over(partition by plan_code order by calendar_month)
  else null end as logo_churn_rate
from base
