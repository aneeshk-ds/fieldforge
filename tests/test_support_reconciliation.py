from datetime import date

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge.reconciliation import support_ticket_counts_match

SEPTEMBER = date(2025, 9, 1)
OCTOBER = date(2025, 10, 1)


@pytest.mark.parametrize("rows, expected", [
    ([(SEPTEMBER, "account", 2), (OCTOBER, "delivery", 1)], True),
    ([(SEPTEMBER, "account", 1), (OCTOBER, "delivery", 2)], False),
    ([(SEPTEMBER, "account", 2)], False),
    ([(SEPTEMBER, "account", 2), (OCTOBER, "delivery", 1), (OCTOBER, "account", 0)], False),
    ([(SEPTEMBER, "account", 2), (SEPTEMBER, "account", 2), (OCTOBER, "delivery", 1)], False),
    ([(SEPTEMBER, "account", None), (OCTOBER, "delivery", 1)], False),
    ([], False),
], ids=["correct", "redistributed-same-total", "missing-group", "extra-group", "duplicate-group", "null-count", "missing-mart-rows"])
def test_support_control_detects_group_errors(tmp_path, rows, expected):
    # Boundary example from FieldForge plus two purpose-built test records.
    tickets = pa.Table.from_pylist([
        {"opened_at": "2025-09-30 18:39:00", "resolved_at": "2025-10-02 10:39:00", "category": "account"},
        {"opened_at": "2025-09-15 12:00:00", "resolved_at": "", "category": "account"},
        {"opened_at": "2025-10-01 12:00:00", "resolved_at": "2025-10-02 12:00:00", "category": "delivery"},
    ])
    path = tmp_path / "tickets.parquet"
    pq.write_table(tickets, path)
    with duckdb.connect() as con:
        con.execute("create table mart_support_health(calendar_month date, category varchar, ticket_count bigint)")
        if rows:
            con.executemany("insert into mart_support_health values (?, ?, ?)", rows)
        assert support_ticket_counts_match(con, path) is expected


def test_support_control_accepts_empty_source_and_mart(tmp_path):
    path = tmp_path / "tickets.parquet"
    pq.write_table(pa.table({"opened_at": pa.array([], type=pa.string()), "category": pa.array([], type=pa.string())}), path)
    with duckdb.connect() as con:
        con.execute("create table mart_support_health(calendar_month date, category varchar, ticket_count bigint)")
        assert support_ticket_counts_match(con, path)
