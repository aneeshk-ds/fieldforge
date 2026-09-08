select * from {{ ref('mart_subscription_health') }} where active_subscribers < 0
