-- Grain: one row per calendar date in the observed reporting window.
-- The window is derived from accepted source events, never hardcoded.
with bounds as (
  select
    least(
      coalesce((select min(paid_at) from {{ ref('stg_invoices') }}), date '9999-12-31'),
      coalesce((select min(cast(ordered_at as date)) from {{ ref('stg_orders') }}), date '9999-12-31'),
      coalesce((select min(start_date) from {{ ref('stg_subscriptions') }}), date '9999-12-31'),
      coalesce((select min(cast(opened_at as date)) from {{ ref('stg_tickets') }}), date '9999-12-31')
    ) as first_date,
    greatest(
      coalesce((select max(paid_at) from {{ ref('stg_invoices') }}), date '1900-01-01'),
      coalesce((select max(cast(ordered_at as date)) from {{ ref('stg_orders') }}), date '1900-01-01'),
      coalesce((select max(start_date) from {{ ref('stg_subscriptions') }}), date '1900-01-01'),
      coalesce((select max(cancelled_at) from {{ ref('stg_subscriptions') }}), date '1900-01-01'),
      coalesce((select max(cast(opened_at as date)) from {{ ref('stg_tickets') }}), date '1900-01-01')
    ) as last_date
), spine as (
  select unnest(generate_series(first_date, last_date, interval 1 day))::date as date_key
  from bounds
)
select
  date_key,
  date_trunc('month', date_key)::date as calendar_month,
  last_day(date_key) as month_end_date,
  year(date_key) as calendar_year,
  quarter(date_key) as calendar_quarter,
  month(date_key) as month_number,
  monthname(date_key) as month_name,
  dayofweek(date_key) as day_of_week_number,
  dayname(date_key) as day_name,
  date_key = last_day(date_key) as is_month_end
from spine
