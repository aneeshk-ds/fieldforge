-- Read unrounded accepted ratings independently of ticket staging.
with tickets as (
  select cast(opened_at as timestamp) opened_at, category,
    nullif(csat, '') raw_rating, try_cast(nullif(csat, '') as double) rating
  from {{ source('silver', 'tickets') }}
), expected as (
  select date_trunc('month', opened_at)::date calendar_month, category,
    count(raw_rating) rated_ticket_count,
    sum(rating) / nullif(count(raw_rating), 0) avg_csat,
    count(*) filter(where raw_rating is not null and
      (rating is null or not isfinite(rating) or rating < 1 or rating > 5 or rating <> floor(rating))) invalid_ratings
  from tickets group by 1, 2
)
select coalesce(e.calendar_month, a.calendar_month) calendar_month,
  coalesce(e.category, a.category) category,
  e.rated_ticket_count expected_rated, a.rated_ticket_count actual_rated,
  e.avg_csat expected_rating, a.avg_csat actual_rating
from expected e
full outer join {{ ref('mart_support_health') }} a using (calendar_month, category)
where e.invalid_ratings > 0
  or e.rated_ticket_count is distinct from a.rated_ticket_count
  or (e.avg_csat is null) <> (a.avg_csat is null)
  or not isfinite(a.avg_csat)
  or a.avg_csat < 1 or a.avg_csat > 5
  or abs(e.avg_csat - a.avg_csat) > 1e-9
