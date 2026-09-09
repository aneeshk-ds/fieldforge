"""A disposable SQL workspace over FieldForge's synthetic quarantine data."""

import duckdb
import streamlit as st

from fieldforge.settings import bronze_dir, gold_dir, quarantine_dir, silver_dir

SOURCE = quarantine_dir() / "orders.parquet"
INCOMING = bronze_dir() / "orders.parquet"
CUSTOMERS = silver_dir() / "customers.parquet"
SUBSCRIPTIONS = silver_dir() / "subscriptions.parquet"
ORDERS = silver_dir() / "orders.parquet"
TICKETS = silver_dir() / "tickets.parquet"
ORDER_LINE_INTEGRITY = gold_dir() / "mart_order_line_integrity.parquet"

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
        f"{integrity_summary[0]:,} accepted orders · {integrity_summary[1]:,} incomplete. "
        "Grain: one row per accepted order. Preview: every incomplete order."
    )
    st.dataframe(
        connection.sql(
            """
            SELECT order_id, currency, header_amount_cents, accepted_line_amount_cents,
                   line_variance_cents, accepted_lines, quarantined_lines_same_order,
                   line_coverage_status
            FROM order_line_integrity
            WHERE line_coverage_status <> 'complete'
            ORDER BY order_id
            """
        ).df(),
        hide_index=True,
        width="stretch",
    )
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
