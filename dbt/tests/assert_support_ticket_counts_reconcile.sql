-- Recompute from accepted silver records, bypassing ticket staging and the mart.
with expected as (
  select date_trunc('month', cast(opened_at as timestamp))::date calendar_month,
    category, count(*) ticket_count
  from {{ source('silver', 'tickets') }}
  group by 1, 2
)
select coalesce(e.calendar_month, a.calendar_month) calendar_month,
  coalesce(e.category, a.category) category,
  e.ticket_count expected_ticket_count, a.ticket_count actual_ticket_count
from expected e
full outer join {{ ref('mart_support_health') }} a using (calendar_month, category)
where e.ticket_count is distinct from a.ticket_count
