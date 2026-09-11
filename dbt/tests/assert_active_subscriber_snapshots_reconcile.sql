with expected as (
  select
    month.calendar_month,
    subscription.plan_code,
    count(*) filter (
      where subscription.start_date <= last_day(month.calendar_month)
        and (
          subscription.cancelled_at is null
          or subscription.cancelled_at >= last_day(month.calendar_month)
        )
    ) as active_subscribers
  from (select distinct calendar_month from {{ ref('dim_date') }}) as month
  cross join {{ ref('stg_subscriptions') }} as subscription
  group by 1, 2
)

select
  expected.calendar_month,
  expected.plan_code,
  expected.active_subscribers as expected_active_subscribers,
  actual.active_subscribers as actual_active_subscribers
from expected
full outer join {{ ref('mart_subscription_health') }} as actual
  using (calendar_month, plan_code)
where expected.active_subscribers is distinct from actual.active_subscribers
