QUERIES = {
    "headline": """select sum(net_revenue_cents) net_revenue_cents,
      sum(transactions) transactions, sum(purchasing_customers) customer_months
      from mart_monthly_kpis""",
    "revenue_trend": """select calendar_month, currency, sum(net_revenue_cents)/100.0 net_revenue
      from mart_monthly_kpis group by 1,2 order by 1,2""",
    "subscriber_trend": """select calendar_month, plan_code, active_subscribers, logo_churn_rate
      from mart_subscription_health order by 1,2""",
    "support": """select calendar_month, category, ticket_count, avg_resolution_hours, avg_csat
      from mart_support_health order by 1,2""",
}
