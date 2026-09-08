select calendar_month, plan_code, count(*) as rows_at_grain
from {{ ref('mart_subscription_health') }}
group by calendar_month, plan_code
having count(*) > 1
