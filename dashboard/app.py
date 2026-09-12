"""FieldForge customer onboarding command center."""

from __future__ import annotations

import html
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data_quality import (
    QualitySnapshot,
    build_timeline,
    evidence_request,
    load_quality_snapshot,
    load_quarantined_record,
)
from dashboard.queries import QUERIES
from fieldforge.settings import data_root, warehouse_path

ROOT = Path(__file__).resolve().parents[1]
DATA = data_root()
DB = warehouse_path()

st.set_page_config(
    page_title="FieldForge · Northstar Commerce",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] { background:
 radial-gradient(circle at 12% -10%, rgba(77,226,211,.15), transparent 30%),
 radial-gradient(circle at 88% 0%, rgba(167,139,250,.13), transparent 32%), #080b12; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1380px; padding-top:2.2rem; padding-bottom:4rem; }
html, body, [class*="css"] { font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; color:#e8edf7; }
h1,h2,h3 { font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif !important; letter-spacing:-.03em; }
.ff-eyebrow { color:#4de2d3; font-size:.72rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
.ff-title { font-size:clamp(2.4rem,5vw,5rem); line-height:.95; font-weight:600; letter-spacing:-.06em; margin:.55rem 0 1rem; max-width:900px; }
.ff-title span { color:#4de2d3; }
.ff-deck { color:#8793a8; font-size:1.05rem; max-width:760px; margin-bottom:1.4rem; }
.ff-status { display:flex; align-items:center; gap:.55rem; color:#c9d2e4; font-size:.82rem; margin-bottom:1.5rem; }
.ff-dot { width:.55rem; height:.55rem; border-radius:50%; background:#4de2d3; box-shadow:0 0 16px #4de2d3; }
.ff-card { min-height:138px; border:1px solid rgba(151,166,196,.16); border-radius:18px; padding:1.25rem;
 background:linear-gradient(145deg,rgba(20,25,38,.88),rgba(12,16,25,.72)); box-shadow:0 22px 50px rgba(0,0,0,.2); }
.ff-card-label { color:#8793a8; font-size:.74rem; letter-spacing:.1em; text-transform:uppercase; }
.ff-card-value { font-size:2rem; font-weight:600; margin:.45rem 0 .25rem; }
.ff-card-note { color:#aab5c8; font-size:.78rem; }
.ff-card--alert .ff-card-value { color:#f6c85f; }
.ff-card--good .ff-card-value { color:#4de2d3; }
.ff-card--compact .ff-card-value { font-size:clamp(1.3rem,2vw,1.8rem); white-space:nowrap; }
.ff-section { margin-top:2.2rem; color:#f3f6fb; }
.ff-kicker { color:#8793a8; margin-top:-.6rem; margin-bottom:1rem; }
.ff-verdict { border-left:3px solid #f6c85f; background:rgba(246,200,95,.07); padding:1rem 1.1rem;
 border-radius:0 14px 14px 0; color:#d9dfeb; margin:1rem 0 1.5rem; }
.ff-investigation { margin-top:1.4rem; border:1px solid rgba(151,166,196,.16); border-radius:18px;
 background:linear-gradient(145deg,rgba(20,25,38,.92),rgba(12,16,25,.78)); padding:1.25rem; }
.ff-investigation-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; margin-bottom:1rem; }
.ff-investigation-status { color:#f6c85f; font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
.ff-timeline { display:grid; grid-template-columns:repeat(3,1fr); gap:.7rem; margin:.7rem 0 1.2rem; }
.ff-event { border:1px solid rgba(151,166,196,.16); border-radius:13px; padding:.85rem; min-height:92px; }
.ff-event--absent,.ff-event--missing { border-style:dashed; background:rgba(246,200,95,.04); }
.ff-event-label { color:#8793a8; font-size:.69rem; letter-spacing:.08em; text-transform:uppercase; }
.ff-event-value { color:#eef3fb; font-size:.9rem; margin-top:.4rem; overflow-wrap:anywhere; }
.ff-event--absent .ff-event-value,.ff-event--missing .ff-event-value { color:#f6c85f; }
.ff-evidence { border-left:3px solid #a78bfa; background:rgba(167,139,250,.07); padding:.85rem 1rem;
 border-radius:0 12px 12px 0; color:#d9dfeb; font-size:.88rem; }
.ff-integrity-primary { border:1px solid rgba(246,200,95,.42); background:rgba(246,200,95,.08);
 border-radius:18px; padding:1.25rem; margin:1rem 0 1.5rem; }
.ff-integrity-primary strong { color:#f6c85f; }
.ff-integrity-primary code { color:#fff; }
.ff-lineage { display:grid; grid-template-columns:1fr auto 1fr auto 1fr auto 1fr; gap:.55rem; align-items:center; margin:1rem 0 2rem; }
.ff-node { background:rgba(19,25,38,.8); border:1px solid rgba(151,166,196,.18); padding:.85rem .65rem; border-radius:12px; text-align:center; color:#cbd5e5; font-size:.77rem; }
.ff-node strong { color:#fff; display:block; font-size:.88rem; margin-bottom:.15rem; }
.ff-arrow { color:#4de2d3; text-align:center; font-size:1.15rem; }
[data-baseweb="tab-list"] { gap:.6rem; border-bottom:1px solid rgba(151,166,196,.14); }
[data-baseweb="tab"] { background:transparent; padding:1rem .35rem; }
[data-baseweb="tab-highlight"] { background-color:#4de2d3; }
[data-testid="stDataFrame"] { border:1px solid rgba(151,166,196,.14); border-radius:14px; overflow:hidden; }
div[data-testid="stSelectbox"] > div > div { background:rgba(18,24,36,.86); }
@media(max-width:800px){.ff-lineage,.ff-timeline{grid-template-columns:1fr}.ff-arrow{transform:rotate(90deg)}.ff-title{font-size:2.8rem}}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def quality_data(fingerprint: tuple[int, ...]) -> QualitySnapshot:
    del fingerprint
    return load_quality_snapshot(DATA)


def pipeline_fingerprint() -> tuple[int, ...]:
    """Invalidate cached controls whenever a durable pipeline output changes."""
    paths = [
        DATA / layer / f"{source}.parquet"
        for layer in ("bronze", "silver", "quarantine")
        for source in ("customers", "subscriptions", "invoices", "orders", "order_items", "tickets")
    ]
    return tuple(path.stat().st_mtime_ns if path.exists() else 0 for path in paths)


def card(label: str, value: str, note: str, tone: str = "") -> None:
    safe = tuple(html.escape(item) for item in (label, value, note))
    st.markdown(
        f'<div class="ff-card {tone}"><div class="ff-card-label">{safe[0]}</div>'
        f'<div class="ff-card-value">{safe[1]}</div><div class="ff-card-note">{safe[2]}</div></div>',
        unsafe_allow_html=True,
    )


def style_figure(figure: go.Figure, height: int = 390) -> go.Figure:
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": "#aab5c8"},
        margin={"l": 12, "r": 12, "t": 42, "b": 12},
        hoverlabel={"bgcolor": "#151b28", "font_color": "#f3f6fb"},
        legend_title_text="",
    )
    figure.update_xaxes(gridcolor="rgba(151,166,196,.10)", zeroline=False)
    figure.update_yaxes(gridcolor="rgba(151,166,196,.10)", zeroline=False)
    return figure


def data_quality_page(snapshot: QualitySnapshot) -> None:
    cols = st.columns(4)
    with cols[0]:
        card("Records received", f"{snapshot.received:,}", "Six operational source extracts")
    with cols[1]:
        card("Accepted", f"{snapshot.accepted:,}", "Available to downstream models", "ff-card--good")
    with cols[2]:
        card("Quarantined", f"{snapshot.quarantined:,}", "Retained with explicit reasons", "ff-card--alert")
    with cols[3]:
        card("Acceptance rate", f"{snapshot.acceptance_rate:.2f}%", "Accepted ÷ received", "ff-card--good")

    verdict = (
        f"Every received record is accounted for. Review the {snapshot.quarantined} retained "
        "exceptions before treating this onboarding run as releasable."
        if snapshot.reconciled
        else "Control totals do not reconcile. Stop downstream release and investigate missing records."
    )
    st.markdown(
        f'<div class="ff-verdict"><strong>Release signal ·</strong> {verdict}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<h3 class="ff-section">Where quality breaks</h3>', unsafe_allow_html=True)
        st.markdown('<div class="ff-kicker">Accepted and quarantined records by source</div>', unsafe_allow_html=True)
        long = snapshot.sources.melt(
            id_vars=["source_label"],
            value_vars=["accepted", "quarantined"],
            var_name="status",
            value_name="records",
        )
        fig = px.bar(
            long,
            y="source_label",
            x="records",
            color="status",
            orientation="h",
            color_discrete_map={"accepted": "#4de2d3", "quarantined": "#f6c85f"},
            category_orders={"source_label": snapshot.sources["source_label"].tolist()[::-1]},
            labels={"source_label": "", "records": "Records"},
        )
        fig.update_traces(hovertemplate="%{y}<br>%{x:,} %{fullData.name}<extra></extra>")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
    with right:
        st.markdown('<h3 class="ff-section">Why records stopped</h3>', unsafe_allow_html=True)
        st.markdown('<div class="ff-kicker">Rule failures requiring source-owner action</div>', unsafe_allow_html=True)
        reasons = snapshot.reasons.sort_values("failures")
        fig = px.bar(
            reasons,
            y="rule_code",
            x="failures",
            orientation="h",
            text="failures",
            color_discrete_sequence=["#a78bfa"],
            labels={"rule_code": "", "failures": "Rule failures"},
        )
        fig.update_traces(textposition="outside", hovertemplate="%{y}<br>%{x} failures<extra></extra>")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})

    st.markdown('<h3 class="ff-section">Exception workbench</h3>', unsafe_allow_html=True)
    st.markdown('<div class="ff-kicker">Filter by source or rule, then inspect the exact record and raw row</div>', unsafe_allow_html=True)
    filter_col, detail_col = st.columns([1, 2.2])
    source_options = ["All sources", *snapshot.sources["source_label"].tolist()]
    with filter_col:
        source_filter = st.selectbox("Source", source_options)
        rules = ["All rules", *snapshot.reasons["rule_code"].tolist()]
        rule_filter = st.selectbox("Rule", rules)
    filtered = snapshot.rejected.copy()
    if source_filter != "All sources":
        filtered = filtered[filtered["source_label"] == source_filter]
    if rule_filter != "All rules":
        filtered = filtered[filtered["rule_code"].str.contains(rule_filter, regex=False)]
    with detail_col:
        st.markdown(
            f"**{len(filtered)} records shown** · Every row remains recoverable in `data/quarantine/`."
        )
        st.dataframe(
            filtered[["source_label", "record_key", "rule_code", "reason", "source_row"]],
            hide_index=True,
            width="stretch",
            column_config={
                "source_label": "Source",
                "record_key": "Record key",
                "rule_code": "Rule",
                "reason": "Reason",
                "source_row": st.column_config.NumberColumn("Raw row", format="%d"),
            },
        )

    if filtered.empty:
        st.info("No quarantined records match these filters.")
        return

    selected_index = st.selectbox(
        "Inspect record",
        filtered.index.tolist(),
        format_func=lambda index: (
            f"{filtered.loc[index, 'record_key']} · {filtered.loc[index, 'source_label']} · "
            f"raw row {int(filtered.loc[index, 'source_row'])}"
        ),
    )
    selected = filtered.loc[selected_index]
    raw_record = load_quarantined_record(
        DATA, str(selected["source"]), int(selected["source_row"])
    )
    timeline = build_timeline(str(selected["source"]), raw_record)
    event_cards = "".join(
        '<div class="ff-event ff-event--{state}"><div class="ff-event-label">{label}</div>'
        '<div class="ff-event-value">{value}</div></div>'.format(
            state=html.escape(event["state"]),
            label=html.escape(event["label"]),
            value=html.escape(event["value"]),
        )
        for event in timeline
    )
    st.markdown(
        '<div class="ff-investigation"><div class="ff-investigation-head">'
        f'<strong>{html.escape(str(selected["record_key"]))}</strong>'
        '<span class="ff-investigation-status">Needs source-owner evidence</span></div>'
        f'<div class="ff-timeline">{event_cards}</div>'
        f'<div class="ff-evidence"><strong>Recommended request ·</strong> '
        f'{html.escape(evidence_request(raw_record))}</div></div>',
        unsafe_allow_html=True,
    )
    visible_record = {
        key: ("—" if pd.isna(value) or str(value).strip() == "" else str(value))
        for key, value in raw_record.items()
        if key not in {"_row_checksum", "_planted_error"}
    }
    with st.expander("View preserved source record and provenance"):
        st.dataframe(
            pd.DataFrame(
                {"Field": list(visible_record), "Preserved value": list(visible_record.values())}
            ),
            hide_index=True,
            width="stretch",
        )


def business_page() -> None:
    if not DB.exists():
        st.info("Gold warehouse not found. Run `make all` to build business models.")
        return
    with duckdb.connect(str(DB), read_only=True) as connection:
        attribution = connection.execute(QUERIES["revenue_attribution"]).df()
        revenue = connection.execute(QUERIES["revenue_trend"]).df()
        subs = connection.execute(QUERIES["subscriber_trend"]).df()
        support = connection.execute(QUERIES["support"]).df()
    st.markdown('<h2 class="ff-section">Business health</h2>', unsafe_allow_html=True)
    st.markdown('<div class="ff-kicker">Governed outputs by currency, plan, and support category</div>', unsafe_allow_html=True)
    st.info(
        "Company revenue includes valid unattributed transactions. Customer-level metrics use only "
        "attributed revenue. Currencies remain separate; no FX conversion has been invented."
    )
    st.markdown("#### Revenue identity coverage")
    coverage_columns = st.columns(len(attribution))
    for column, row in zip(coverage_columns, attribution.itertuples(index=False), strict=True):
        with column:
            card(
                f"{row.currency} company net",
                f"{row.currency} {row.company_net_revenue:,.2f}",
                f"{row.currency} {row.unattributed_net_revenue:,.2f} unattributed · "
                f"{row.attribution_rate:.2f}% attributed",
                "ff-card--good ff-card--compact"
                if row.attribution_rate >= 95
                else "ff-card--alert ff-card--compact",
            )
    coverage = px.bar(
        attribution,
        x="currency",
        y="attribution_rate",
        text=attribution["attribution_rate"].map(lambda value: f"{value:.2f}%"),
        color_discrete_sequence=["#a78bfa"],
        labels={"currency": "Transaction currency", "attribution_rate": "Revenue attributed (%)"},
    )
    coverage.update_yaxes(range=[0, 100])
    coverage.update_traces(textposition="outside", hovertemplate="%{x}<br>%{y:.2f}% attributed<extra></extra>")
    st.plotly_chart(style_figure(coverage, 330), width="stretch", config={"displayModeBar": False})
    st.markdown("#### Company revenue trend")
    fig = px.line(
        revenue,
        x="calendar_month",
        y="net_revenue",
        color="currency",
        markers=True,
        color_discrete_sequence=["#4de2d3", "#a78bfa", "#f6c85f"],
        labels={"calendar_month": "Month", "net_revenue": "Net revenue"},
    )
    st.plotly_chart(style_figure(fig, 430), width="stretch", config={"displayModeBar": False})
    left, right = st.columns(2)
    with left:
        fig = px.line(
            subs,
            x="calendar_month",
            y="active_subscribers",
            color="plan_code",
            labels={"calendar_month": "Month", "active_subscribers": "Active subscribers"},
            color_discrete_sequence=["#4de2d3", "#a78bfa", "#f6c85f"],
        )
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
    with right:
        support = support.assign(resolution_time_label=support["avg_resolution_hours"].map(
            lambda value: "Not available" if pd.isna(value) else f"{value:,.2f} h"
        ), satisfaction_label=support["avg_csat"].map(
            lambda value: "Not available" if pd.isna(value) else f"{value:.2f} / 5"
        ))
        fig = px.bar(
            support,
            custom_data=["resolved_ticket_count", "resolution_time_label", "rated_ticket_count", "satisfaction_label"],
            x="calendar_month",
            y="ticket_count",
            color="category",
            labels={"calendar_month": "Opening month", "ticket_count": "Accepted tickets opened", "category": "Category"},
            color_discrete_sequence=["#4de2d3", "#a78bfa", "#f6c85f", "#ff7e8a"],
        )
        fig.update_yaxes(tickformat=",d", rangemode="tozero")
        fig.update_traces(hovertemplate="Opening month: %{x|%b %Y}<br>Accepted tickets opened: %{y:,.0f}<br>Completed tickets: %{customdata[0]:,.0f}<br>Avg resolution (completed only): %{customdata[1]}<br>Rated tickets: %{customdata[2]:,.0f}<br>Avg satisfaction: %{customdata[3]}<extra>%{fullData.name}</extra>")
        st.plotly_chart(style_figure(fig), width="stretch", config={"displayModeBar": False})
        st.caption("Counted in the month opened, including unresolved tickets. Quarantined tickets are excluded; empty month/category groups are omitted. Hover for average elapsed resolution time and its completed-ticket count. Unresolved tickets have no completed duration; zero-hour resolutions count. Later resolutions can update an earlier month’s average.")
        st.caption("Satisfaction averages recorded ratings out of 5, with the rated-ticket count shown on hover. Missing ratings are excluded; no ratings means Not available. This describes responding tickets, not the percentage of satisfied customers. Later feedback can update an earlier opening month.")


def order_integrity_page() -> None:
    if not DB.exists():
        st.info("Gold warehouse not found. Run `make all` to build order-line integrity.")
        return
    with duckdb.connect(str(DB), read_only=True) as connection:
        integrity = connection.execute(QUERIES["order_line_integrity"]).df()

    incomplete = integrity[integrity["line_coverage_status"] != "complete"].copy()
    known = incomplete[incomplete["line_coverage_status"] == "incomplete_quarantined_line"]
    unexplained = incomplete[incomplete["line_coverage_status"] == "incomplete_unexplained_line"]

    st.markdown('<h2 class="ff-section">Order-line integrity</h2>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ff-kicker">Does each accepted order header reconcile to its accepted lines?</div>',
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    with columns[0]:
        card("Accepted orders", f"{len(integrity):,}", "One row per accepted order", "ff-card--good")
    with columns[1]:
        card(
            "Known quarantine impact",
            f"{len(known):,}",
            "Variance linked to retained rejection evidence",
            "ff-card--alert",
        )
    with columns[2]:
        card(
            "Unexplained gaps",
            f"{len(unexplained):,}",
            "Secondary source-owner investigation backlog",
            "ff-card--compact",
        )

    if not known.empty:
        primary = known.iloc[0]
        st.markdown(
            '<div class="ff-integrity-primary"><strong>Primary action · known quarantine consequence</strong><br>'
            f'Order <code>{html.escape(str(primary["order_id"]))}</code> is short by '
            f'{html.escape(str(primary["currency"]))} {primary["line_variance"]:,.2f} in accepted lines. '
            f'{int(primary["quarantined_lines_same_order"])} retained quarantined line explains the gap; '
            'review that evidence before releasing line-level reporting.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Incomplete accepted orders")
    st.dataframe(
        incomplete[
            [
                "order_id",
                "currency",
                "header_amount",
                "accepted_line_amount",
                "line_variance",
                "accepted_lines",
                "quarantined_lines_same_order",
                "line_coverage_status",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "order_id": "Order",
            "currency": "Currency",
            "header_amount": st.column_config.NumberColumn("Header amount", format="%.2f"),
            "accepted_line_amount": st.column_config.NumberColumn(
                "Accepted-line amount", format="%.2f"
            ),
            "line_variance": st.column_config.NumberColumn("Variance", format="%.2f"),
            "accepted_lines": "Accepted lines",
            "quarantined_lines_same_order": "Quarantined lines",
            "line_coverage_status": "Coverage status",
        },
    )
    st.caption(
        "Known quarantine impact is shown first by learner decision. Unexplained gaps remain visible "
        "and are never silently treated as complete."
    )
def governance_page(snapshot: QualitySnapshot) -> None:
    st.markdown('<h2 class="ff-section">Lineage & governance</h2>', unsafe_allow_html=True)
    st.markdown('<div class="ff-kicker">How raw customer data becomes a decision-ready metric</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="ff-lineage">
 <div class="ff-node"><strong>Sources</strong>CRM · Billing · Storefront · Support</div><div class="ff-arrow">→</div>
 <div class="ff-node"><strong>Bronze</strong>Original values and provenance</div><div class="ff-arrow">→</div>
 <div class="ff-node"><strong>Silver</strong>Validated, standardized, identity-linked</div><div class="ff-arrow">→</div>
 <div class="ff-node"><strong>Gold</strong>Tested dimensions, facts, KPI marts</div>
</div>
""",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("#### Current run")
        st.code(snapshot.run_id, language=None)
        st.write(f"Ingested: `{snapshot.ingested_at}`")
        st.write("Control: `bronze = silver + quarantine` for every source")
    with right:
        st.markdown("#### Governed paths")
        st.write("Rules: `config/planted_errors.yml` and `fieldforge/pipeline.py`")
        st.write("Metrics: `config/kpis.yml` and `dbt/models/marts/`")
        st.write("Evidence: `artifacts/validation_summary.json` and `artifacts/reconciliation.json`")
    with st.expander("View dashboard SQL traceability"):
        st.code(QUERIES["revenue_trend"], language="sql")


st.markdown('<div class="ff-eyebrow">FieldForge / Northstar Commerce</div>', unsafe_allow_html=True)
st.markdown('<div class="ff-title">Turn messy customer data into <span>trusted decisions.</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ff-deck">An operational command center for onboarding quality, governed analytics, and explainable customer identity.</div>',
    unsafe_allow_html=True,
)

try:
    snapshot = quality_data(pipeline_fingerprint())
except FileNotFoundError as error:
    st.error(f"{error}. Run `make pipeline` from the repository root, then refresh this page.")
    st.stop()

status = "CONTROL TOTALS RECONCILED" if snapshot.reconciled else "CONTROL FAILURE"
st.markdown(
    f'<div class="ff-status"><span class="ff-dot"></span>{status} · RUN {html.escape(snapshot.run_id[:8])}</div>',
    unsafe_allow_html=True,
)

quality_tab, integrity_tab, business_tab, governance_tab = st.tabs(
    ["Data quality", "Order integrity", "Business health", "Lineage & governance"]
)
with quality_tab:
    data_quality_page(snapshot)
with integrity_tab:
    order_integrity_page()
with business_tab:
    business_page()
with governance_tab:
    governance_page(snapshot)
