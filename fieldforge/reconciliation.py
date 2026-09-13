"""Independent checks against accepted source records, separate from dbt SQL."""

from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime
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


def logo_churn_matches(con: duckdb.DuckDBPyConnection, silver: Path) -> bool:
    """Rebuild the complete month/plan series from accepted Parquet, without dbt inputs.

    The observed window includes invoice payments, order placements, ticket openings,
    subscription starts and (for its upper bound) cancellations, as governed by dim_date.
    Count subscriptions, not distinct customers; month-end cancellations remain active.
    """
    starts = []
    ends = []
    subscriptions = []
    for source, fields in (
        ("invoices", ["paid_at"]),
        ("orders", ["ordered_at"]),
        ("tickets", ["opened_at"]),
        ("subscriptions", ["start_date", "cancelled_at", "plan_code"]),
    ):
        for row in pq.read_table(silver / f"{source}.parquet", columns=fields).to_pylist():
            event = date.fromisoformat(str(row[fields[0]])[:10])
            starts.append(event)
            ends.append(event)
            if source == "subscriptions":
                cancelled = row["cancelled_at"]
                cancelled = None if cancelled in (None, "") else date.fromisoformat(str(cancelled)[:10])
                if cancelled is not None:
                    ends.append(cancelled)
                subscriptions.append((row["plan_code"], event, cancelled))
    expected = {}
    if starts:
        month = min(starts).replace(day=1)
        final_month = max(ends).replace(day=1)
        plans = {plan for plan, _, _ in subscriptions}
        previous = {}
        while month <= final_month:
            month_end = month.replace(day=monthrange(month.year, month.month)[1])
            for plan in plans:
                records = [(start, cancel) for code, start, cancel in subscriptions if code == plan]
                active = sum(start <= month_end and (cancel is None or cancel >= month_end) for start, cancel in records)
                churned = sum(cancel is not None and cancel.replace(day=1) == month for _, cancel in records)
                denominator = previous.get(plan, 0)
                rate = churned / denominator if denominator > 0 else None
                expected[(month, plan)] = (active, churned, rate)
                previous[plan] = active
            month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
    rows = con.execute("select calendar_month, plan_code, active_subscribers, churned_subscribers, logo_churn_rate from mart_subscription_health").fetchall()
    actual = {(month, plan): (active, churned, rate) for month, plan, active, churned, rate in rows}
    if len(actual) != len(rows) or actual.keys() != expected.keys():
        return False
    for key, (active, churned, rate) in expected.items():
        actual_active, actual_churned, actual_rate = actual[key]
        if (actual_active, actual_churned) != (active, churned):
            return False
        if rate is None:
            if actual_rate is not None:
                return False
        elif actual_rate is None or not isfinite(actual_rate) or not isclose(actual_rate, rate, rel_tol=1e-12, abs_tol=1e-12):
            return False
    return True


def monthly_revenue_matches(con: duckdb.DuckDBPyConnection, silver: Path) -> bool:
    """Rebuild every month/type/currency group from accepted Parquet only."""

    def integer(value):
        try:
            parsed = Decimal(str(value))
        except InvalidOperation:
            return None
        if not parsed.is_finite() or parsed != parsed.to_integral_value():
            return None
        return int(parsed)

    crosswalk = {}
    for row in pq.read_table(
        silver / "identity_crosswalk.parquet",
        columns=["source_system", "source_identity", "customer_sk"],
    ).to_pylist():
        key = (row["source_system"], row["source_identity"])
        if key in crosswalk:
            return False
        crosswalk[key] = row["customer_sk"]

    expected = {}
    revenue_ids = set()
    sources = (
        (
            "invoices",
            "subscription",
            "invoice_id",
            "billing_customer_id",
            "paid_at",
            "gross_amount_cents",
            "subscriptions",
        ),
        (
            "orders",
            "one_off",
            "order_id",
            "storefront_customer_id",
            "ordered_at",
            "order_amount_cents",
            "orders",
        ),
    )
    for source, revenue_type, id_field, identity_field, date_field, gross_field, system in sources:
        fields = [
            id_field,
            identity_field,
            date_field,
            gross_field,
            "refund_amount_cents",
            "currency",
        ]
        if source == "orders":
            fields.append("status")
        for row in pq.read_table(silver / f"{source}.parquet", columns=fields).to_pylist():
            if source == "orders" and row["status"] == "cancelled":
                continue
            revenue_id = row[id_field]
            if revenue_id in revenue_ids:
                return False
            revenue_ids.add(revenue_id)
            try:
                month = date.fromisoformat(str(row[date_field])[:10]).replace(day=1)
            except ValueError:
                return False
            gross = integer(row[gross_field])
            refund = integer(row["refund_amount_cents"])
            if gross is None or refund is None:
                return False
            customer = crosswalk.get((system, row[identity_field]))
            attributed = customer not in (None, "")
            key = (month, revenue_type, row["currency"])
            values = expected.setdefault(
                key,
                {
                    "transactions": 0,
                    "gross": 0,
                    "refund": 0,
                    "net": 0,
                    "attributed_net": 0,
                    "unattributed_net": 0,
                    "attributed_transactions": 0,
                    "unattributed_transactions": 0,
                    "customers": set(),
                },
            )
            net = gross - refund
            values["transactions"] += 1
            values["gross"] += gross
            values["refund"] += refund
            values["net"] += net
            bucket = "attributed" if attributed else "unattributed"
            values[f"{bucket}_net"] += net
            values[f"{bucket}_transactions"] += 1
            if attributed:
                values["customers"].add(customer)

    rows = con.execute(
        """select calendar_month, revenue_type, currency, transactions,
                  gross_revenue_cents, refund_amount_cents, net_revenue_cents,
                  attributed_net_revenue_cents, unattributed_net_revenue_cents,
                  attributed_transactions, unattributed_transactions,
                  revenue_attribution_rate, purchasing_customers
           from mart_monthly_kpis"""
    ).fetchall()
    actual = {(row[0], row[1], row[2]): row[3:] for row in rows}
    if len(actual) != len(rows) or actual.keys() != expected.keys():
        return False
    for key, values in expected.items():
        row = actual[key]
        expected_exact = (
            values["transactions"],
            values["gross"],
            values["refund"],
            values["net"],
            values["attributed_net"],
            values["unattributed_net"],
            values["attributed_transactions"],
            values["unattributed_transactions"],
        )
        if row[:8] != expected_exact or row[9] != len(values["customers"]):
            return False
        expected_rate = (
            None if values["net"] == 0 else 100.0 * values["attributed_net"] / values["net"]
        )
        actual_rate = row[8]
        if expected_rate is None:
            if actual_rate is not None:
                return False
        elif actual_rate is None or not isfinite(actual_rate) or not isclose(
            actual_rate, expected_rate, rel_tol=1e-12, abs_tol=1e-9
        ):
            return False
    return True


def order_kpis_match(
    con: duckdb.DuckDBPyConnection, silver: Path, quarantine: Path
) -> bool:
    """Rebuild accepted-line population and every order-integrity row from Parquet."""

    def integer(value):
        try:
            parsed = Decimal(str(value))
        except InvalidOperation:
            return None
        if not parsed.is_finite() or parsed != parsed.to_integral_value():
            return None
        return int(parsed)

    orders = {}
    for row in pq.read_table(
        silver / "orders.parquet",
        columns=["order_id", "ordered_at", "status", "order_amount_cents", "currency"],
    ).to_pylist():
        order_id = row["order_id"]
        amount = integer(row["order_amount_cents"])
        if order_id in orders or amount is None:
            return False
        try:
            order_date = date.fromisoformat(str(row["ordered_at"])[:10])
        except ValueError:
            return False
        orders[order_id] = (order_date, row["currency"], row["status"], amount)

    source_lines = {}
    line_totals = defaultdict(int)
    line_counts = Counter()
    for row in pq.read_table(
        silver / "order_items.parquet",
        columns=["order_id", "line_number", "quantity", "unit_price_cents"],
    ).to_pylist():
        line_number = integer(row["line_number"])
        quantity = integer(row["quantity"])
        unit_price = integer(row["unit_price_cents"])
        if None in (line_number, quantity, unit_price):
            return False
        key = (row["order_id"], line_number)
        if key in source_lines:
            return False
        extended = quantity * unit_price
        link_status = "linked" if row["order_id"] in orders else "order_not_accepted"
        source_lines[key] = (extended, link_status)
        if link_status == "linked":
            line_totals[row["order_id"]] += extended
            line_counts[row["order_id"]] += 1

    fact_rows = con.execute(
        "select order_id, line_number, extended_amount_cents, order_link_status "
        "from fct_order_item"
    ).fetchall()
    fact_lines = {
        (order_id, line_number): (amount, link_status)
        for order_id, line_number, amount, link_status in fact_rows
    }
    if len(fact_lines) != len(fact_rows) or fact_lines != source_lines:
        return False

    quarantined_counts = Counter(
        row["order_id"]
        for row in pq.read_table(
            quarantine / "order_items.parquet", columns=["order_id"]
        ).to_pylist()
    )
    expected = {}
    for order_id, (order_date, currency, status, header_amount) in orders.items():
        accepted_amount = line_totals[order_id]
        variance = header_amount - accepted_amount
        quarantined_lines = quarantined_counts[order_id]
        if variance < 0:
            return False
        if variance == 0:
            coverage = "complete"
        elif quarantined_lines:
            coverage = "incomplete_quarantined_line"
        else:
            coverage = "incomplete_unexplained_line"
        expected[order_id] = (
            order_date,
            currency,
            status,
            header_amount,
            accepted_amount,
            variance,
            line_counts[order_id],
            quarantined_lines,
            coverage,
        )

    mart_rows = con.execute(
        """select order_id, order_date, currency, order_status,
                  header_amount_cents, accepted_line_amount_cents,
                  line_variance_cents, accepted_lines,
                  quarantined_lines_same_order, line_coverage_status
           from mart_order_line_integrity"""
    ).fetchall()
    actual = {row[0]: row[1:] for row in mart_rows}
    return len(actual) == len(mart_rows) and actual == expected
