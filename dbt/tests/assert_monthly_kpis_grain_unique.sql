select calendar_month, revenue_type, currency, count(*) as rows_at_grain
from {{ ref('mart_monthly_kpis') }}
group by calendar_month, revenue_type, currency
having count(*) > 1
