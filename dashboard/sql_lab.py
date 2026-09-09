"""A disposable SQL workspace over FieldForge's governed local data."""

import json
import tomllib
from importlib import metadata

import duckdb
import streamlit as st

from fieldforge.settings import (
    ROOT,
    artifacts_root,
    bronze_dir,
    gold_dir,
    quarantine_dir,
    silver_dir,
)

SOURCE = quarantine_dir() / "orders.parquet"
INCOMING = bronze_dir() / "orders.parquet"
BRONZE_SOURCES = {
    source: bronze_dir() / f"{source}.parquet"
    for source in ("customers", "subscriptions", "invoices", "orders", "order_items", "tickets")
}
CUSTOMERS = silver_dir() / "customers.parquet"
SUBSCRIPTIONS = silver_dir() / "subscriptions.parquet"
ORDERS = silver_dir() / "orders.parquet"
TICKETS = silver_dir() / "tickets.parquet"
ORDER_LINE_INTEGRITY = gold_dir() / "mart_order_line_integrity.parquet"
BENCHMARK_RESULTS = [
    artifacts_root() / "benchmarks" / profile / "benchmark.json"
    for profile in ("1x", "10x")
]
SPARK_PARITY_RESULT = artifacts_root() / "spark_parity.json"

st.set_page_config(page_title="FieldForge SQL Lab", page_icon="🔎", layout="wide")
st.title("FieldForge · SQL Lab")
st.caption("Northstar Commerce / Synthetic data / DuckDB SQL")
required_sources = (
    SOURCE,
    INCOMING,
    CUSTOMERS,
    SUBSCRIPTIONS,
    ORDERS,
    TICKETS,
    ORDER_LINE_INTEGRITY,
    *BRONZE_SOURCES.values(),
)
if not all(path.exists() for path in required_sources):
    st.error("Run make pipeline from the FieldForge folder to prepare the data.")
    st.stop()

with duckdb.connect() as connection:
    connection.execute(
        "CREATE TABLE quarantined_orders AS SELECT order_id, currency, "
        "_rule_codes AS rejection_code, _rejection_reasons AS rejection_reason "
        "FROM read_parquet(?)",
        [str(SOURCE)],
    )
    connection.execute(
        "CREATE TABLE incoming_orders AS SELECT order_id, currency FROM read_parquet(?)",
        [str(INCOMING)],
    )
    connection.execute(
        """
        CREATE TABLE source_scale_profile AS
        SELECT 'customers' AS source, COUNT(*) AS records FROM read_parquet(?)
        UNION ALL SELECT 'subscriptions', COUNT(*) FROM read_parquet(?)
        UNION ALL SELECT 'invoices', COUNT(*) FROM read_parquet(?)
        UNION ALL SELECT 'orders', COUNT(*) FROM read_parquet(?)
        UNION ALL SELECT 'order_items', COUNT(*) FROM read_parquet(?)
        UNION ALL SELECT 'tickets', COUNT(*) FROM read_parquet(?)
        """,
        [str(path) for path in BRONZE_SOURCES.values()],
    )
    connection.execute(
        """
        CREATE TABLE customer_chronology AS
        WITH customer_events AS (
            SELECT normalized_email, 'subscription' AS first_event_type,
                   subscription_id AS first_event_id, CAST(start_date AS TIMESTAMP) AS first_event_at
            FROM read_parquet(?)
            UNION ALL
            SELECT normalized_email, 'order', order_id, CAST(ordered_at AS TIMESTAMP)
            FROM read_parquet(?)
            UNION ALL
            SELECT normalized_email, 'support_ticket', ticket_id, CAST(opened_at AS TIMESTAMP)
            FROM read_parquet(?)
        ),
        first_events AS (
            SELECT normalized_email, first_event_type, first_event_id, first_event_at
            FROM customer_events
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY normalized_email
                ORDER BY first_event_at, first_event_type, first_event_id
            ) = 1
        )
        SELECT
            customer.crm_customer_id,
            CAST(customer.created_at AS TIMESTAMP) AS created_at,
            event.first_event_type,
            event.first_event_id,
            event.first_event_at,
            DATE_DIFF('day', event.first_event_at, CAST(customer.created_at AS TIMESTAMP)) AS days_late,
            CASE
                WHEN event.first_event_at IS NULL THEN 'no_events'
                WHEN CAST(customer.created_at AS TIMESTAMP) <= event.first_event_at THEN 'valid'
                ELSE 'created_after_first_event'
            END AS chronology_status
        FROM read_parquet(?) AS customer
        LEFT JOIN first_events AS event USING (normalized_email)
        """,
        [str(SUBSCRIPTIONS), str(ORDERS), str(TICKETS), str(CUSTOMERS)],
    )
    connection.execute(
        """
        CREATE TABLE order_line_integrity AS
        SELECT order_id, currency, header_amount_cents, accepted_line_amount_cents,
               line_variance_cents, accepted_lines, quarantined_lines_same_order,
               line_coverage_status
        FROM read_parquet(?)
        """,
        [str(ORDER_LINE_INTEGRITY)],
    )
    connection.execute("SET enable_external_access = false")
    preview = connection.sql("SELECT * FROM quarantined_orders ORDER BY order_id").df()
    st.subheader("Your table: quarantined_orders")
    st.write("One row per rejected order. All four columns are VARCHAR (text). order_id identifies the order.")
    st.dataframe(preview, hide_index=True, width="stretch")
    st.subheader("Your table: incoming_orders")
    incoming_count = connection.sql("SELECT COUNT(*) FROM incoming_orders").fetchone()[0]
    st.write(
        f"{incoming_count:,} rows · One row per incoming order, including orders later quarantined. "
        "Columns: order_id and currency, both VARCHAR (text). Preview: first five rows."
    )
    st.dataframe(
        connection.sql("SELECT * FROM incoming_orders ORDER BY order_id LIMIT 5").df(),
        hide_index=True,
        width="stretch",
    )
    st.subheader("Your table: source_scale_profile")
    source_total = connection.sql("SELECT SUM(records) FROM source_scale_profile").fetchone()[0]
    st.write(
        f"{source_total:,} generated source records. Grain: one row per source extract. "
        "This is the current 500-customer baseline, before any larger benchmark run."
    )
    st.dataframe(
        connection.sql("SELECT source, records FROM source_scale_profile ORDER BY source").df(),
        hide_index=True,
        width="stretch",
    )
    if all(path.exists() for path in BENCHMARK_RESULTS):
        benchmark_rows = []
        for path in BENCHMARK_RESULTS:
            result = json.loads(path.read_text())
            benchmark_rows.append(
                {
                    "profile": result["profile"],
                    "cache_state": result["cache_state"],
                    "customers": result["customers"],
                    "source_rows": result["total_source_rows"],
                    "source_to_silver_seconds": result["timings"][
                        "source_to_silver_seconds"
                    ],
                    "dbt_build_seconds": result["timings"]["dbt_build_seconds"],
                    "total_seconds": result["timings"]["total_seconds"],
                    "orchestrator_peak_rss_mib": result["environment"][
                        "orchestrator_peak_rss_mib"
                    ],
                    "child_peak_rss_mib": result["environment"][
                        "completed_children_peak_rss_mib"
                    ],
                }
            )
        st.subheader("Your table: benchmark_results")
        st.write(
            "Two isolated, seeded benchmark runs on this Mac. Grain: one row per scale "
            "profile. Memory columns are separate per-process peaks and must not be added."
        )
        st.dataframe(benchmark_rows, hide_index=True, width="stretch")
    if SPARK_PARITY_RESULT.exists():
        parity = json.loads(SPARK_PARITY_RESULT.read_text())
        st.subheader("Your table: runtime_parity")
        st.write(
            "One executed engine comparison at accepted-order grain. The canonical result is "
            "FieldForge's trusted Python/Pandera output; Spark reimplements the same rules. "
            "Zero missing and unexpected IDs means the actual order IDs match."
        )
        st.dataframe(
            [
                {
                    "engine": f"PySpark {parity['pyspark_version']}",
                    "java": parity["java_version"],
                    "canonical_accepted_orders": parity["expected_orders"],
                    "spark_accepted_orders": parity["accepted_orders"],
                    "missing_order_ids": parity["missing_order_ids"],
                    "unexpected_order_ids": parity["unexpected_order_ids"],
                    "status": parity["status"],
                }
            ],
            hide_index=True,
            width="stretch",
        )
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    direct_dependencies = []
    for requirement in project["dependencies"]:
        package, declared_version = requirement.split("==", maxsplit=1)
        installed_name = package.split("[", maxsplit=1)[0]
        direct_dependencies.append(
            {
                "package": package,
                "declared_version": declared_version,
                "installed_version": metadata.version(installed_name),
                "relationship": "direct",
            }
        )
    installed_count = len(list(metadata.distributions()))
    locked_count = len(tomllib.loads((ROOT / "uv.lock").read_text())["package"])
    st.subheader("Your table: dependency_inventory")
    st.write(
        f"{len(direct_dependencies)} direct packages are declared, while {installed_count} "
        f"distributions are installed and {locked_count} cross-platform packages are resolved "
        "in uv.lock. Grain: one row per direct project dependency."
    )
    st.dataframe(direct_dependencies, hide_index=True, width="stretch")
    st.subheader("Your table: customer_chronology")
    chronology_summary = connection.sql(
        """
        SELECT
            COUNT(*) FILTER (WHERE first_event_at IS NOT NULL) AS customers_with_events,
            COUNT(*) FILTER (WHERE chronology_status = 'created_after_first_event') AS affected_customers
        FROM customer_chronology
        """
    ).fetchone()
    st.write(
        f"{chronology_summary[0]:,} customers with an event · "
        f"{chronology_summary[1]:,} currently violate first-seen chronology. "
        "Grain: one row per accepted CRM customer. Preview: eight customers closest to the boundary."
    )
    st.dataframe(
        connection.sql(
            """
            SELECT crm_customer_id, created_at, first_event_type, first_event_id,
                   first_event_at, days_late, chronology_status
            FROM customer_chronology
            WHERE first_event_at IS NOT NULL
            ORDER BY days_late DESC, crm_customer_id
            LIMIT 8
            """
        ).df(),
        hide_index=True,
        width="stretch",
    )
    st.subheader("Your table: order_line_integrity")
    integrity_summary = connection.sql(
        """
        SELECT COUNT(*) AS accepted_orders,
               COUNT(*) FILTER (WHERE line_coverage_status <> 'complete') AS incomplete_orders
        FROM order_line_integrity
        """
    ).fetchone()
    st.write(
        f"This table checks whether each order's product rows add up to its recorded total. "
        f"It contains {integrity_summary[0]:,} accepted orders; {integrity_summary[1]:,} do not "
        "currently add up. Only those three problem orders are shown below."
    )
    st.info(
        "What to do for ORD-0000015: ask the storefront owner to fix and resend the rejected "
        "product row. Keep the recorded USD 90.00 order total unless the owner proves that "
        "total is wrong."
    )
    integrity_preview = connection.sql(
            """
            SELECT order_id, header_amount_cents, accepted_line_amount_cents,
                   line_variance_cents, line_coverage_status
            FROM order_line_integrity
            WHERE line_coverage_status <> 'complete'
            ORDER BY order_id
            """
        ).df()
    integrity_preview["line_coverage_status"] = integrity_preview[
        "line_coverage_status"
    ].replace(
        {
            "incomplete_quarantined_line": "incomplete — rejected product row found",
            "incomplete_unexplained_line": "incomplete — cause not yet linked",
        }
    )
    st.dataframe(
        integrity_preview,
        hide_index=True,
        width="stretch",
    )
    st.write(
        "SQL names used below: `header_amount_cents` is the recorded order total; "
        "`accepted_line_amount_cents` is the total of product rows FieldForge accepted."
    )
    st.subheader("Exercise 6 · Check one order total")
    st.write(
        "Use SQL to select ORD-0000015 from order_line_integrity. Show order_id and calculate "
        "header_amount_cents minus accepted_line_amount_cents. Name the calculated column "
        "difference_cents."
    )
    order_check_query = st.text_area(
        "Write the order-check SQL",
        height=160,
        placeholder="SELECT ...",
        key="order_check_query",
    )
    if st.button("Run order check", type="primary"):
        try:
            statements = connection.extract_statements(order_check_query)
            if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
                st.warning("Enter one SELECT query. This workspace only reads project data.")
            else:
                result = connection.execute(order_check_query).fetchdf()
                st.success(f"Query ran successfully · {len(result)} result rows")
                st.dataframe(result, hide_index=True, width="stretch")
        except duckdb.Error as error:
            st.error(str(error))
    st.subheader("Exercise 5 · Calculate the quarantine rate")
    st.write(
        "Return one row with one column named quarantine_rate_pct. Calculate quarantined "
        "orders as a percentage of all incoming orders using a count subquery for each "
        "table. Use 100.0 to convert to a percentage; do not type either row count. "
        "For this exercise, incoming_orders is nonempty. No sorting is needed."
    )
    query = st.text_area("Write your SQL", height=200, placeholder="Write your query here…")
    if st.button("Run query", type="primary"):
        try:
            statements = connection.extract_statements(query)
            if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
                st.warning("Enter one SELECT query. This workspace is for reading the practice table.")
            else:
                result = connection.execute(query).fetchdf()
                st.success(f"Query ran successfully · {len(result)} result rows")
                st.dataframe(result, hide_index=True, width="stretch")
        except duckdb.Error as error:
            st.error(str(error))
    st.caption("Each run uses a temporary copy. Your queries do not modify the pipeline files.")
