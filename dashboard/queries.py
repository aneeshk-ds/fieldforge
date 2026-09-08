QUERIES = {
    "headline": """select currency, sum(net_revenue_cents) net_revenue_cents,
      sum(attributed_net_revenue_cents) attributed_net_revenue_cents,
      sum(unattributed_net_revenue_cents) unattributed_net_revenue_cents,
      sum(transactions) transactions, sum(unattributed_transactions) unattributed_transactions
      from mart_monthly_kpis group by 1 order by 1""",
    "revenue_trend": """select calendar_month, currency, sum(net_revenue_cents)/100.0 net_revenue
      from mart_monthly_kpis group by 1,2 order by 1,2""",
    "revenue_attribution": """select currency,
      sum(net_revenue_cents)/100.0 company_net_revenue,
      sum(attributed_net_revenue_cents)/100.0 attributed_net_revenue,
      sum(unattributed_net_revenue_cents)/100.0 unattributed_net_revenue,
      100.0*sum(attributed_net_revenue_cents)/nullif(sum(net_revenue_cents),0) attribution_rate
      from mart_monthly_kpis group by 1 order by 1""",
    "subscriber_trend": """select calendar_month, plan_code, active_subscribers, logo_churn_rate
      from mart_subscription_health order by 1,2""",
    "support": """select calendar_month, category, ticket_count, avg_resolution_hours, avg_csat
      from mart_support_health order by 1,2""",
}
