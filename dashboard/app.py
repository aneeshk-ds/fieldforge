import sys
from pathlib import Path

import duckdb
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard.queries import QUERIES

DB = Path(__file__).resolve().parents[1] / "data" / "fieldforge.duckdb"
st.set_page_config(page_title="FieldForge | Northstar Commerce", layout="wide")
st.title("Northstar Commerce — Customer & Revenue Health")
st.caption("Synthetic data • governed gold models • no paid services")

if not DB.exists():
    st.error("Warehouse not found. Run `make all` first.")
    st.stop()
con = duckdb.connect(str(DB), read_only=True)
headline = con.execute(QUERIES["headline"]).df().iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Net revenue (mixed currency)", f"{headline.net_revenue_cents / 100:,.0f}")
c2.metric("Transactions", f"{headline.transactions:,.0f}")
c3.metric("Customer-month observations", f"{headline.customer_months:,.0f}")
st.warning("Revenue is segmented by currency; the headline is operational and not FX-converted.")
revenue = con.execute(QUERIES["revenue_trend"]).df()
st.plotly_chart(px.line(revenue, x="calendar_month", y="net_revenue", color="currency", markers=True, title="Monthly net revenue by currency"), use_container_width=True)
left, right = st.columns(2)
subs = con.execute(QUERIES["subscriber_trend"]).df()
left.plotly_chart(px.line(subs, x="calendar_month", y="active_subscribers", color="plan_code", title="Active subscribers at month end"), use_container_width=True)
support = con.execute(QUERIES["support"]).df()
right.plotly_chart(px.bar(support, x="calendar_month", y="ticket_count", color="category", title="Support demand"), use_container_width=True)
with st.expander("Metric traceability"):
    st.code(QUERIES["revenue_trend"], language="sql")
    st.markdown("Definitions: `config/kpis.yml`. Model: `dbt/models/marts/mart_monthly_kpis.sql`.")
