with customer_events as (
  select normalized_email, cast(start_date as timestamp) as event_at
  from {{ ref('stg_subscriptions') }}
  union all
  select normalized_email, ordered_at
  from {{ ref('stg_orders') }}
  union all
  select normalized_email, opened_at
  from {{ ref('stg_tickets') }}
),
first_events as (
  select normalized_email, min(event_at) as first_event_at
  from customer_events
  group by normalized_email
)
select customers.crm_customer_id, customers.created_at, first_events.first_event_at
from {{ ref('stg_customers') }} as customers
join first_events using (normalized_email)
where customers.created_at > first_events.first_event_at
