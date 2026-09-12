-- Grain: one row per ticket-opening calendar_month and support category.
-- ticket_count includes every accepted ticket, regardless of resolution or identity.
select date_trunc('month', opened_at)::date calendar_month, category,
  count(*) ticket_count,
  count(resolved_at) resolved_ticket_count,
  avg(epoch(resolved_at - opened_at) / 3600.0) filter(where resolved_at is not null) avg_resolution_hours,
  avg(csat) filter(where csat is not null) avg_csat
from {{ ref('stg_tickets') }} group by 1,2
