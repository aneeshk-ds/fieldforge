from __future__ import annotations

import re
from datetime import UTC, datetime

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from fieldforge.settings import (
    artifacts_root,
    bronze_dir,
    ensure_directories,
    quarantine_dir,
    silver_dir,
    source_dir,
)
from fieldforge.utils import normalize_email, normalize_phone, stable_hash, write_json

SOURCES = ("customers", "subscriptions", "invoices", "orders", "order_items", "tickets")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def profile_sources() -> dict:
    ensure_directories()
    report = {}
    for name in SOURCES:
        df = pd.read_csv(source_dir() / f"{name}.csv")
        report[name] = {"rows": len(df), "columns": len(df.columns), "nulls": {c: int(df[c].isna().sum()) for c in df}, "distinct": {c: int(df[c].nunique(dropna=True)) for c in df}}
    write_json(artifacts_root() / "source_profile.json", report)
    return report


def ingest_bronze(run_id: str) -> None:
    ensure_directories()
    for name in SOURCES:
        path = source_dir() / f"{name}.csv"
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df.insert(0, "_source_row_number", range(2, len(df) + 2))
        df["_source_file"] = path.name
        df["_ingested_at_utc"] = datetime.now(UTC).isoformat()
        df["_run_id"] = run_id
        df["_row_checksum"] = df.apply(lambda row: stable_hash(*row.astype(str).tolist()), axis=1)
        df.to_parquet(bronze_dir() / f"{name}.parquet", index=False)


def _reasons(name: str, row: pd.Series, context: dict) -> list[tuple[str, str]]:
    result = []
    def add(condition: bool, code: str, reason: str) -> None:
        if condition:
            result.append((code, reason))
    if name == "customers":
        add(not bool(EMAIL.match(str(row.email).strip())), "CUSTOMER_EMAIL_INVALID", "email is malformed")
        add(not str(row.country).strip(), "CUSTOMER_COUNTRY_MISSING", "country is required")
        add(context["customer_ids"].get(row.crm_customer_id, 0) > 1, "CUSTOMER_ID_DUPLICATE", "crm_customer_id is not unique")
    elif name == "subscriptions":
        add(row.plan_code not in {"ESSENTIALS", "PLUS", "PREMIUM"}, "SUBSCRIPTION_PLAN_UNKNOWN", "plan_code is unsupported")
        add(bool(row.cancelled_at) and pd.to_datetime(row.cancelled_at) < pd.to_datetime(row.start_date), "SUBSCRIPTION_DATES_INVALID", "cancelled_at precedes start_date")
    elif name == "invoices":
        gross, refund = int(row.gross_amount_cents), int(row.refund_amount_cents)
        add(gross < 0, "INVOICE_GROSS_NEGATIVE", "gross amount cannot be negative")
        add(refund > gross, "INVOICE_REFUND_EXCESS", "refund exceeds gross amount")
    elif name == "orders":
        add(row.currency not in {"USD", "CAD", "GBP"}, "ORDER_CURRENCY_UNSUPPORTED", "currency is unsupported")
        add(bool(row.delivered_at) and pd.to_datetime(row.delivered_at) < pd.to_datetime(row.ordered_at), "ORDER_DATES_INVALID", "delivered_at precedes ordered_at")
        add(not (str(row.customer_email).strip() or str(row.storefront_customer_id).strip()), "ORDER_IDENTITY_MISSING", "customer email and source id are both missing")
    elif name == "order_items":
        add(int(row.quantity) <= 0, "ORDER_ITEM_QUANTITY_INVALID", "quantity must be positive")
        add(row.order_id not in context["order_ids"], "ORDER_ITEM_ORPHAN", "order_id does not exist")
    elif name == "tickets":
        add(bool(row.resolved_at) and pd.to_datetime(row.resolved_at) < pd.to_datetime(row.opened_at), "TICKET_DATES_INVALID", "resolved_at precedes opened_at")
        add(bool(row.csat) and not 1 <= int(float(row.csat)) <= 5, "TICKET_CSAT_INVALID", "csat must be from 1 through 5")
    return result


def validate_silver() -> dict:
    frames = {name: pd.read_parquet(bronze_dir() / f"{name}.parquet") for name in SOURCES}
    context = {"customer_ids": frames["customers"]["crm_customer_id"].value_counts().to_dict(), "order_ids": set(frames["orders"]["order_id"])}
    summary = {}
    for name, df in frames.items():
        valid_rows, invalid_rows = [], []
        for _, row in df.iterrows():
            failures = _reasons(name, row, context)
            if failures:
                rejected = row.to_dict()
                rejected["_rule_codes"] = "|".join(x[0] for x in failures)
                rejected["_rejection_reasons"] = "|".join(x[1] for x in failures)
                rejected["_raw_key"] = str(row.get({"customers": "crm_customer_id", "subscriptions": "subscription_id", "invoices": "invoice_id", "orders": "order_id", "order_items": "order_id", "tickets": "ticket_id"}[name], ""))
                invalid_rows.append(rejected)
            else:
                valid_rows.append(row.to_dict())
        valid = pd.DataFrame(valid_rows, columns=df.columns)
        invalid = pd.DataFrame(invalid_rows)
        if "email" in valid:
            valid["normalized_email"] = valid["email"].map(normalize_email)
        if "customer_email" in valid:
            valid["normalized_email"] = valid["customer_email"].map(normalize_email)
        if "requester_email" in valid:
            valid["normalized_email"] = valid["requester_email"].map(normalize_email)
        if "phone" in valid:
            valid["normalized_phone"] = valid["phone"].map(normalize_phone)
        valid.to_parquet(silver_dir() / f"{name}.parquet", index=False)
        if invalid.empty:
            invalid = pd.DataFrame(columns=list(df.columns) + ["_rule_codes", "_rejection_reasons", "_raw_key"])
        pq.write_table(pa.Table.from_pandas(invalid, preserve_index=False), quarantine_dir() / f"{name}.parquet")
        summary[name] = {"bronze": len(df), "accepted": len(valid), "quarantined": len(invalid), "reconciled": len(df) == len(valid) + len(invalid)}
    write_json(artifacts_root() / "validation_summary.json", summary)
    return summary


def resolve_identities() -> pd.DataFrame:
    customers = pd.read_parquet(silver_dir() / "customers.parquet")
    canonical = {row.normalized_email: stable_hash("customer", row.normalized_email)[:16] for _, row in customers.iterrows()}
    rows = []
    for source, key_col in (("customers", "crm_customer_id"), ("subscriptions", "billing_customer_id"), ("orders", "storefront_customer_id"), ("tickets", "ticket_id")):
        df = pd.read_parquet(silver_dir() / f"{source}.parquet")
        for _, row in df.iterrows():
            email = row.get("normalized_email")
            cid = canonical.get(email)
            rows.append({"source_system": source, "source_identity": row[key_col], "customer_sk": cid, "match_method": "normalized_email_exact" if cid else "unmatched", "confidence": 1.0 if cid else 0.0, "normalized_email": email})
    crosswalk = pd.DataFrame(rows).drop_duplicates(["source_system", "source_identity"])
    crosswalk.to_parquet(silver_dir() / "identity_crosswalk.parquet", index=False)
    return crosswalk
