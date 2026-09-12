-- Compare all cancellation groups and rates against accepted subscription dates.
with subscriptions as (
  select plan_code, cast(start_date as date) start_date,
    try_cast(nullif(cancelled_at, '') as date) cancelled_at
  from {{ source('silver', 'subscriptions') }}
), counts as (
  select m.calendar_month, s.plan_code,
    count(*) filter (where s.start_date <= last_day(m.calendar_month)
      and (s.cancelled_at is null or s.cancelled_at >= last_day(m.calendar_month))) active,
    count(*) filter (where date_trunc('month', s.cancelled_at) = m.calendar_month) churned
  from (select distinct calendar_month from {{ ref('dim_date') }}) m
  cross join subscriptions s group by 1, 2
), denominators as (
  select *, lag(active) over (partition by plan_code order by calendar_month) prior_active
  from counts
), expected as (
  select *, case when prior_active > 0 then churned::double / prior_active else null end rate
  from denominators
)
select e.calendar_month expected_month, a.calendar_month actual_month,
  e.plan_code expected_plan, a.plan_code actual_plan
from expected e full outer join {{ ref('mart_subscription_health') }} a
  using (calendar_month, plan_code)
where e.calendar_month is null or a.calendar_month is null
  or e.active is distinct from a.active_subscribers
  or e.churned is distinct from a.churned_subscribers
  or (e.rate is null) <> (a.logo_churn_rate is null)
  or not isfinite(a.logo_churn_rate)
  or abs(e.rate - a.logo_churn_rate) > 1e-12
