"""Independent checks against accepted source records, separate from dbt SQL."""

from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import isclose, isfinite
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


def support_resolution_matches(con: duckdb.DuckDBPyConnection, tickets_path: Path) -> bool:
    """Recompute opening-cohort completed counts and means with Python timedeltas."""
    durations = defaultdict(list)
    for ticket in pq.read_table(tickets_path, columns=["opened_at", "resolved_at", "category"]).to_pylist():
        opened = datetime.fromisoformat(str(ticket["opened_at"]))
        values = durations[(opened.date().replace(day=1), ticket["category"])]
        if ticket["resolved_at"] not in (None, ""):
            resolved = datetime.fromisoformat(str(ticket["resolved_at"]))
            hours = (resolved - opened).total_seconds() / 3600
            if hours < 0:
                return False
            values.append(hours)
    rows = con.execute(
        "select calendar_month, category, resolved_ticket_count, avg_resolution_hours from mart_support_health"
    ).fetchall()
    actual = {(month, category): (count, mean) for month, category, count, mean in rows}
    if len(actual) != len(rows) or actual.keys() != durations.keys():
        return False
    for key, values in durations.items():
        count, mean = actual[key]
        if count != len(values):
            return False
        if not values:
            if mean is not None:
                return False
        elif mean is None or not isfinite(mean) or not isclose(
            mean, sum(values) / len(values), rel_tol=1e-12, abs_tol=1e-9
        ):
            return False
    return True


def support_satisfaction_matches(con: duckdb.DuckDBPyConnection, tickets_path: Path) -> bool:
    """Recompute rating counts and means from accepted raw values, without staging casts."""
    ratings = defaultdict(list)
    for ticket in pq.read_table(tickets_path, columns=["opened_at", "category", "csat"]).to_pylist():
        month = datetime.fromisoformat(str(ticket["opened_at"])).date().replace(day=1)
        values = ratings[(month, ticket["category"])]
        if ticket["csat"] in (None, ""):
            continue
        try:
            rating = Decimal(str(ticket["csat"]))
        except InvalidOperation:
            return False
        if not rating.is_finite() or not 1 <= rating <= 5 or rating != rating.to_integral_value():
            return False
        values.append(rating)
    rows = con.execute("select calendar_month, category, rated_ticket_count, avg_csat from mart_support_health").fetchall()
    actual = {(month, category): (count, mean) for month, category, count, mean in rows}
    if len(actual) != len(rows) or actual.keys() != ratings.keys():
        return False
    for key, values in ratings.items():
        count, mean = actual[key]
        if count != len(values):
            return False
        if not values:
            if mean is not None:
                return False
        elif mean is None or not isfinite(mean) or not isclose(
            mean, float(sum(values) / len(values)), rel_tol=1e-12, abs_tol=1e-9
        ):
            return False
    return True
