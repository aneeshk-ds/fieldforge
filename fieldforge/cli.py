from __future__ import annotations

import argparse
import shutil
import time
import uuid

import duckdb

from fieldforge.generate import generate
from fieldforge.pipeline import ingest_bronze, profile_sources, resolve_identities, validate_silver
from fieldforge.settings import ARTIFACTS, DATA, GOLD, WAREHOUSE, ensure_directories
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
    with duckdb.connect(str(WAREHOUSE), read_only=True) as con:
        models = [x[0] for x in con.execute("select table_name from information_schema.tables where table_schema='main' and table_name like 'mart_%'").fetchall()]
        for model in models:
            con.execute(f"COPY {model} TO '{GOLD / (model + '.parquet')}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE 1)")
    print(f"Exported {len(models)} gold marts")


def reconcile() -> None:
    with duckdb.connect(str(WAREHOUSE), read_only=True) as con:
        checks = {
            "all_invoice_net_cents": con.execute("select coalesce(sum(gross_amount_cents-refund_amount_cents),0) from stg_invoices").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='subscription'").fetchone()[0],
            "all_order_net_cents": con.execute("select coalesce(sum(order_amount_cents-refund_amount_cents),0) from stg_orders where status <> 'cancelled'").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='one_off'").fetchone()[0],
            "attributed_invoice_net_cents": con.execute("""select coalesce(sum(i.gross_amount_cents-i.refund_amount_cents),0) from stg_invoices i join read_parquet('data/silver/identity_crosswalk.parquet') x on x.source_system='subscriptions' and x.source_identity=i.billing_customer_id where x.customer_sk is not null""").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='subscription' and attribution_status='attributed'").fetchone()[0],
            "attributed_order_net_cents": con.execute("""select coalesce(sum(o.order_amount_cents-o.refund_amount_cents),0) from stg_orders o join read_parquet('data/silver/identity_crosswalk.parquet') x on x.source_system='orders' and x.source_identity=o.storefront_customer_id where o.status <> 'cancelled' and x.customer_sk is not null""").fetchone()[0] == con.execute("select coalesce(sum(net_revenue_cents),0) from fct_revenue where revenue_type='one_off' and attribution_status='attributed'").fetchone()[0],
            "attribution_partition": con.execute("select count(*)=0 from mart_monthly_kpis where net_revenue_cents <> attributed_net_revenue_cents + unattributed_net_revenue_cents or transactions <> attributed_transactions + unattributed_transactions").fetchone()[0],
            "attributed_customer_fk": con.execute("select count(*)=0 from fct_revenue f left join dim_customer d using(customer_sk) where f.attribution_status='attributed' and d.customer_sk is null").fetchone()[0],
            "unattributed_customer_null": con.execute("select count(*)=0 from fct_revenue where attribution_status='unattributed' and customer_sk is not null").fetchone()[0],
        }
    write_json(ARTIFACTS / "reconciliation.json", checks)
    if not all(checks.values()):
        raise SystemExit(f"Reconciliation failed: {checks}")
    print("Reconciliation passed")


def dashboard_check() -> None:
    from dashboard.queries import QUERIES
    with duckdb.connect(str(WAREHOUSE), read_only=True) as con:
        for _name, query in QUERIES.items():
            con.execute(query).fetchone()
    print(f"Dashboard smoke check passed ({len(QUERIES)} queries)")


def clean() -> None:
    for path in (DATA, ARTIFACTS):
        if path.exists():
            shutil.rmtree(path)
    print("Removed generated data and artifacts")


def benchmark() -> None:
    started = time.perf_counter()
    run_pipeline(20260907, 500)
    payload = {"stage": "pre_dbt_pipeline", "customers": 500, "elapsed_seconds": round(time.perf_counter() - started, 3)}
    write_json(ARTIFACTS / "benchmark.json", payload)
    print(payload)


def main() -> None:
    parser = argparse.ArgumentParser(prog="fieldforge")
    sub = parser.add_subparsers(dest="command", required=True)
    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("--seed", type=int, default=20260907)
    pipeline.add_argument("--customers", type=int, default=500)
    for command in ("export-gold", "reconcile", "dashboard-check", "clean", "benchmark"):
        sub.add_parser(command)
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
        benchmark()


if __name__ == "__main__":
    main()
