"""Independent checks against accepted source records, separate from dbt SQL."""

from collections import Counter
from datetime import datetime
from pathlib import Path

import duckdb
import pyarrow.parquet as pq


def support_ticket_counts_match(con: duckdb.DuckDBPyConnection, tickets_path: Path) -> bool:
    """Compare every opening-month/category group, including missing or duplicate groups."""
    tickets = pq.read_table(tickets_path, columns=["opened_at", "category"]).to_pylist()
    expected = Counter(
        (datetime.fromisoformat(str(ticket["opened_at"])).date().replace(day=1), ticket["category"])
        for ticket in tickets
    )
    rows = con.execute(
        "select calendar_month, category, ticket_count from mart_support_health"
    ).fetchall()
    actual = {(month, category): count for month, category, count in rows}
    return len(actual) == len(rows) and dict(expected) == actual
