select *
from {{ ref('mart_monthly_kpis') }}
where net_revenue_cents
  <> attributed_net_revenue_cents + unattributed_net_revenue_cents
   or transactions <> attributed_transactions + unattributed_transactions
