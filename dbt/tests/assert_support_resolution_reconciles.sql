-- Accepted source records, independently of ticket staging; preserve all-unresolved groups.
with tickets as (
  select cast(opened_at as timestamp) opened_at,
    try_cast(nullif(resolved_at, '') as timestamp) resolved_at, category
  from {{ source('silver', 'tickets') }}
), expected as (
  select date_trunc('month', opened_at)::date calendar_month, category,
    count(resolved_at) resolved_ticket_count,
    sum(epoch(resolved_at - opened_at)) / 3600.0 / nullif(count(resolved_at), 0) avg_resolution_hours
  from tickets group by 1, 2
)
select coalesce(e.calendar_month, a.calendar_month) calendar_month,
  coalesce(e.category, a.category) category,
  e.resolved_ticket_count expected_completed, a.resolved_ticket_count actual_completed,
  e.avg_resolution_hours expected_hours, a.avg_resolution_hours actual_hours
from expected e
full outer join {{ ref('mart_support_health') }} a using (calendar_month, category)
where e.resolved_ticket_count is distinct from a.resolved_ticket_count
  or (e.avg_resolution_hours is null) <> (a.avg_resolution_hours is null)
  or not isfinite(a.avg_resolution_hours)
  or a.avg_resolution_hours < 0
  or abs(e.avg_resolution_hours - a.avg_resolution_hours) > 1e-9
