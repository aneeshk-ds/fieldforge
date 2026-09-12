from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from fieldforge.generate import generate
from fieldforge.pipeline import ingest_bronze, profile_sources, resolve_identities, validate_silver
from fieldforge.reconciliation import support_resolution_matches, support_ticket_counts_match
from fieldforge.settings import (
    ROOT,
    artifacts_root,
    data_root,
    ensure_directories,
    gold_dir,
    is_isolated,
    silver_dir,
    warehouse_path,
)
from fieldforge.utils import write_json


def run_pipeline(seed: int, customers: int) -> None:
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"fieldforge:{seed}:{customers}"))
    generate(seed, customers)
    profile_sources()
    ingest_bronze(run_id)
    summary = validate_silver()
    resolve_identities()
    assert all(x["reconciled"] for x in summary.values()), "bronze/silver/quarantine mismatch"
    print(f"Pre-dbt pipeline complete: run_id={run_id}")


def export_gold() -> None:
    ensure_directories()
    with duckdb.connect(str(warehouse_path()), read_only=True) as con:
        models = [x[0] for x in con.execute("select table_name from information_schema.tables where table_schema='main' and table_name like 'mart_%'").fetchall()]
        for model in models:
            con.execute(f"COPY {model} TO '{gold_dir() / (model + '.parquet')}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")
    print(f"Exported {len(models)} gold marts")


def reconcile() -> None:
    with duckdb.connect(str(warehouse_path()), read_only=True) as con:
        checks = {
            "support_tickets_opened": support_ticket_counts_match(con, silver_dir() / "tickets.parquet"),
            "support_resolution_hours": support_resolution_matches(con, silver_dir() / "tickets.parquet"),
            "all_invoice_net_cents": con.execute("select coalesce(sum(gross_amount_cents-refund_amount_cents),0) from stg_invoices").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='subscription'").fetchone()[0],
            "all_order_net_cents": con.execute("select coalesce(sum(order_amount_cents-refund_amount_cents),0) from stg_orders where status <> 'cancelled'").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='one_off'").fetchone()[0],
            "attributed_invoice_net_cents": con.execute("""select coalesce(sum(i.gross_amount_cents-i.refund_amount_cents),0) from stg_invoices i join stg_identity_crosswalk x on x.source_system='subscriptions' and x.source_identity=i.billing_customer_id where x.customer_sk is not null""").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='subscription' and attribution_status='attributed'").fetchone()[0],
            "attributed_order_net_cents": con.execute("""select coalesce(sum(o.order_amount_cents-o.refund_amount_cents),0) from stg_orders o join stg_identity_crosswalk x on x.source_system='orders' and x.source_identity=o.storefront_customer_id where o.status <> 'cancelled' and x.customer_sk is not null""").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='one_off' and attribution_status='attributed'").fetchone()[0],
            "attribution_partition": con.execute("select count(*)=0 from mart_monthly_kpis where net_revenue_cents <> attributed_net_revenue_cents + unattributed_net_revenue_cents or transactions <> attributed_transactions + unattributed_transactions").fetchone()[0],
            "attributed_customer_fk": con.execute("select count(*)=0 from fct_revenue f left join dim_customer d using(customer_sk) where f.attribution_status='attributed' and d.customer_sk is null").fetchone()[0],
            "unattributed_customer_null": con.execute("select count(*)=0 from fct_revenue where attribution_status='unattributed' and customer_sk is not null").fetchone()[0],
            "order_item_row_parity": con.execute("select (select count(*) from fct_order_item) = (select count(*) from stg_order_items)").fetchone()[0],
            "order_item_grain_unique": con.execute("select count(*)=0 from (select order_id, line_number from fct_order_item group by 1,2 having count(*)>1)").fetchone()[0],
            "order_item_product_fk": con.execute("select count(*)=0 from fct_order_item f left join dim_product p using(product_sk) where p.product_sk is null").fetchone()[0],
            "order_line_variance_explained": con.execute("select (select count(*) from mart_order_line_integrity where line_coverage_status='incomplete_unexplained_line') <= (select count(*) from stg_quarantined_order_items where _rule_codes like '%ORDER_ITEM_ORPHAN%')").fetchone()[0],
            "revenue_date_dimension_fk": con.execute("select count(*)=0 from fct_revenue f left join dim_date d on d.date_key = f.recognized_date where d.date_key is null").fetchone()[0],
            "active_subscriber_snapshots": con.execute("""
                with expected as (
                    select m.calendar_month, s.plan_code,
                        count(*) filter (
                            where s.start_date <= last_day(m.calendar_month)
                            and (s.cancelled_at is null or s.cancelled_at >= last_day(m.calendar_month))
                        ) active_subscribers
                    from (select distinct calendar_month from dim_date) m
                    cross join stg_subscriptions s
                    group by 1, 2
                )
                select count(*)=0
                from expected e
                full outer join mart_subscription_health a using(calendar_month, plan_code)
                where e.active_subscribers is distinct from a.active_subscribers
            """).fetchone()[0],
            "customer_chronology": con.execute("""
                with customer_events as (
                    select normalized_email, cast(start_date as timestamp) event_at from stg_subscriptions
                    union all
                    select normalized_email, ordered_at from stg_orders
                    union all
                    select normalized_email, opened_at from stg_tickets
                ), first_events as (
                    select normalized_email, min(event_at) first_event_at
                    from customer_events group by normalized_email
                )
                select count(*)=0
                from stg_customers c join first_events e using(normalized_email)
                where c.created_at > e.first_event_at
            """).fetchone()[0],
        }
    write_json(artifacts_root() / "reconciliation.json", checks)
    if not all(checks.values()):
        raise SystemExit(f"Reconciliation failed: {checks}")
    print("Reconciliation passed")


def dashboard_check() -> None:
    from dashboard.queries import QUERIES
    with duckdb.connect(str(warehouse_path()), read_only=True) as con:
        for _name, query in QUERIES.items():
            con.execute(query).fetchone()
    print(f"Dashboard smoke check passed ({len(QUERIES)} queries)")


def clean() -> None:
    for path in (data_root(), artifacts_root()):
        if path.exists():
            shutil.rmtree(path)
    print("Removed generated data and artifacts")


def _rss_mib(peak: int) -> float:
    bytes_used = peak if sys.platform == "darwin" else peak * 1024
    return round(bytes_used / (1024 * 1024), 2)


def benchmark(profile: str, seed: int, customers: int) -> None:
    if not (
        is_isolated()
        and os.environ.get("FIELDFORGE_DATA_ROOT")
        and os.environ.get("FIELDFORGE_ARTIFACTS_ROOT")
    ):
        raise SystemExit(
            "Benchmark roots must be relocated with FIELDFORGE_DATA_ROOT and "
            "FIELDFORGE_ARTIFACTS_ROOT."
        )

    cache_state = "warm" if warehouse_path().exists() else "cold"
    previous_benchmark = artifacts_root() / "benchmark.json"
    if previous_benchmark.exists():
        previous = json.loads(previous_benchmark.read_text())
        previous_stamp = previous["started_at_utc"].replace(":", "").replace("+00:00", "Z")
        write_json(artifacts_root() / f"benchmark-{previous_stamp}.json", previous)
    started_at = datetime.now(UTC)
    total_started = time.perf_counter()
    timings: dict[str, float] = {}

    stage_started = time.perf_counter()
    run_pipeline(seed, customers)
    timings["source_to_silver_seconds"] = round(time.perf_counter() - stage_started, 3)

    stage_started = time.perf_counter()
    dbt_executable = str(Path(sys.executable).with_name("dbt"))
    subprocess.run(
        [dbt_executable, "build", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        cwd=ROOT,
        check=True,
        env=os.environ.copy(),
    )
    timings["dbt_build_seconds"] = round(time.perf_counter() - stage_started, 3)

    stage_started = time.perf_counter()
    export_gold()
    timings["gold_export_seconds"] = round(time.perf_counter() - stage_started, 3)

    stage_started = time.perf_counter()
    reconcile()
    dashboard_check()
    timings["verification_seconds"] = round(time.perf_counter() - stage_started, 3)
    timings["total_seconds"] = round(time.perf_counter() - total_started, 3)

    manifest = json.loads((artifacts_root() / "synthetic_manifest.json").read_text())
    dbt_manifest = json.loads((ROOT / "dbt" / "target" / "manifest.json").read_text())
    nodes = dbt_manifest["nodes"].values()
    payload = {
        "profile": profile,
        "seed": seed,
        "customers": customers,
        "cache_state": cache_state,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "logical_cpu_count": os.cpu_count(),
            "orchestrator_peak_rss_mib": _rss_mib(
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            ),
            "completed_children_peak_rss_mib": _rss_mib(
                resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            ),
            "memory_scope": (
                "Per-process peaks for the Python orchestrator and completed child processes; "
                "not a concurrent system-wide peak."
            ),
        },
        "row_counts": manifest["row_counts"],
        "total_source_rows": sum(manifest["row_counts"].values()),
        "dbt_models": sum(node["resource_type"] == "model" for node in nodes),
        "dbt_tests": sum(node["resource_type"] == "test" for node in nodes),
        "timings": timings,
        "data_root": str(data_root()),
        "artifacts_root": str(artifacts_root()),
        "claim_boundary": "Single-host benchmark; not a production throughput or capacity claim.",
    }
    write_json(artifacts_root() / "benchmark.json", payload)
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="fieldforge")
    sub = parser.add_subparsers(dest="command", required=True)
    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("--seed", type=int, default=20260907)
    pipeline.add_argument("--customers", type=int, default=500)
    for command in ("export-gold", "reconcile", "dashboard-check", "clean"):
        sub.add_parser(command)
    benchmark_parser = sub.add_parser("benchmark")
    benchmark_parser.add_argument("--profile", default="1x")
    benchmark_parser.add_argument("--seed", type=int, default=20260907)
    benchmark_parser.add_argument("--customers", type=int, default=500)
    args = parser.parse_args()
    if args.command == "pipeline":
        run_pipeline(args.seed, args.customers)
    elif args.command == "export-gold":
        export_gold()
    elif args.command == "reconcile":
        reconcile()
    elif args.command == "dashboard-check":
        dashboard_check()
    elif args.command == "clean":
        clean()
    elif args.command == "benchmark":
        benchmark(args.profile, args.seed, args.customers)


if __name__ == "__main__":
    main()
