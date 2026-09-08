select calendar_month, category, count(*) as rows_at_grain
from {{ ref('mart_support_health') }}
group by calendar_month, category
having count(*) > 1
