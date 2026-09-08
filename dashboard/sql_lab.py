"""A disposable SQL workspace over FieldForge's synthetic quarantine data."""

import duckdb
import streamlit as st

from fieldforge.settings import bronze_dir, quarantine_dir

SOURCE = quarantine_dir() / "orders.parquet"
INCOMING = bronze_dir() / "orders.parquet"

st.set_page_config(page_title="FieldForge SQL Lab", page_icon="🔎", layout="wide")
st.title("FieldForge · SQL Lab")
st.caption("Northstar Commerce / Synthetic data / DuckDB SQL")
if not SOURCE.exists() or not INCOMING.exists():
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
    connection.execute("SET enable_external_access = false")
    preview = connection.sql("SELECT * FROM quarantined_orders ORDER BY order_id").df()
    st.subheader("Your table: quarantined_orders")
    st.write("One row per rejected order. All four columns are VARCHAR (text). order_id identifies the order.")
    st.dataframe(preview, hide_index=True, use_container_width=True)
    st.subheader("Your table: incoming_orders")
    incoming_count = connection.sql("SELECT COUNT(*) FROM incoming_orders").fetchone()[0]
    st.write(
        f"{incoming_count:,} rows · One row per incoming order, including orders later quarantined. "
        "Columns: order_id and currency, both VARCHAR (text). Preview: first five rows."
    )
    st.dataframe(
        connection.sql("SELECT * FROM incoming_orders ORDER BY order_id LIMIT 5").df(),
        hide_index=True,
        use_container_width=True,
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
                st.dataframe(result, hide_index=True, use_container_width=True)
        except duckdb.Error as error:
            st.error(str(error))
    st.caption("Each run uses a temporary copy. Your queries do not modify the pipeline files.")
