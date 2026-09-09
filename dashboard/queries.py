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
    "order_line_integrity": """select order_id, currency,
      header_amount_cents/100.0 header_amount,
      accepted_line_amount_cents/100.0 accepted_line_amount,
      line_variance_cents/100.0 line_variance,
      accepted_lines, quarantined_lines_same_order, line_coverage_status
      from mart_order_line_integrity
      order by case line_coverage_status
        when 'incomplete_quarantined_line' then 1
        when 'incomplete_unexplained_line' then 2
        else 3 end, order_id""",
}
