"""Data access and reconciliation helpers for the operational dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

SOURCES = (
    ("customers", "CRM customers"),
    ("subscriptions", "Subscriptions"),
    ("invoices", "Invoices"),
    ("orders", "Orders"),
    ("order_items", "Order items"),
    ("tickets", "Support tickets"),
)

TIMELINE_FIELDS = {
    "customers": (("created_at", "Customer created"),),
    "subscriptions": (
        ("start_date", "Subscription started"),
        ("cancelled_at", "Subscription cancelled"),
    ),
    "invoices": (("paid_at", "Invoice paid"), ("refunded_at", "Refunded")),
    "orders": (
        ("ordered_at", "Order placed"),
        ("dispatched_at", "Dispatched"),
        ("delivered_at", "Delivered"),
    ),
    "tickets": (("opened_at", "Ticket opened"), ("resolved_at", "Ticket resolved")),
}


@dataclass(frozen=True)
class QualitySnapshot:
    sources: pd.DataFrame
    reasons: pd.DataFrame
    rejected: pd.DataFrame
    received: int
    accepted: int
    quarantined: int
    acceptance_rate: float
    reconciled: bool
    run_id: str
    ingested_at: str


def load_quarantined_record(root: Path, source: str, source_row: int) -> dict[str, object]:
    """Return one original quarantined row, including provenance and rejection metadata."""
    valid_sources = {name for name, _ in SOURCES}
    if source not in valid_sources:
        raise ValueError(f"Unknown source: {source}")
    path = root / "data" / "quarantine" / f"{source}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing pipeline output: {path}")
    with duckdb.connect() as connection:
        frame = connection.execute(
            "SELECT * FROM read_parquet(?) WHERE _source_row_number = ?",
            [str(path), source_row],
        ).df()
    if len(frame) != 1:
        raise LookupError(f"Expected one {source} record at source row {source_row}; found {len(frame)}")
    return frame.iloc[0].to_dict()


def build_timeline(source: str, record: dict[str, object]) -> list[dict[str, str]]:
    """Describe available, missing, and contract-absent events for a source record."""
    events = []
    for field, label in TIMELINE_FIELDS.get(source, ()):
        if field not in record:
            events.append({"field": field, "label": label, "value": "Not supplied", "state": "absent"})
            continue
        value = record[field]
        if pd.isna(value) or str(value).strip() == "":
            events.append({"field": field, "label": label, "value": "Missing", "state": "missing"})
            continue
        events.append({"field": field, "label": label, "value": str(value), "state": "available"})
    return events


def evidence_request(record: dict[str, object]) -> str:
    """Give the smallest useful source-owner request for the failed rule."""
    rule_codes = str(record.get("_rule_codes", ""))
    record_key = str(record.get("_raw_key", "record"))
    if "ORDER_DATES_INVALID" in rule_codes:
        return (
            f"Request the original placement, dispatch, and delivery events for {record_key}, "
            "including timestamps, timezones, event IDs, and audit history. Do not correct either "
            "date until the source sequence is confirmed."
        )
    if "TICKET_DATES_INVALID" in rule_codes or "SUBSCRIPTION_DATES_INVALID" in rule_codes:
        return (
            f"Request the complete source event history for {record_key}, including timestamps, "
            "timezones, and the system audit trail before correcting chronology."
        )
    return (
        f"Request the authoritative source record and audit history for {record_key}; confirm the "
        "failed fields with the source owner before correction or release."
    )


def load_quality_snapshot(root: Path) -> QualitySnapshot:
    """Read durable lakehouse outputs and calculate the current-run control totals."""
    data = root / "data"
    rows: list[dict[str, object]] = []
    rejected_frames: list[pd.DataFrame] = []

    with duckdb.connect() as connection:
        for source, label in SOURCES:
            bronze = data / "bronze" / f"{source}.parquet"
            silver = data / "silver" / f"{source}.parquet"
            quarantine = data / "quarantine" / f"{source}.parquet"
            for path in (bronze, silver, quarantine):
                if not path.exists():
                    raise FileNotFoundError(f"Missing pipeline output: {path}")

            received = connection.execute(
                "SELECT count(*) FROM read_parquet(?)", [str(bronze)]
            ).fetchone()[0]
            accepted = connection.execute(
                "SELECT count(*) FROM read_parquet(?)", [str(silver)]
            ).fetchone()[0]
            quarantined = connection.execute(
                "SELECT count(*) FROM read_parquet(?)", [str(quarantine)]
            ).fetchone()[0]
            rows.append(
                {
                    "source": source,
                    "source_label": label,
                    "received": received,
                    "accepted": accepted,
                    "quarantined": quarantined,
                    "acceptance_rate": 100 * accepted / received if received else 0.0,
                    "reconciled": received == accepted + quarantined,
                }
            )
            rejected = connection.execute(
                """
                SELECT ? AS source, ? AS source_label, _raw_key AS record_key,
                       _rule_codes AS rule_code, _rejection_reasons AS reason,
                       _source_row_number AS source_row, _run_id AS run_id
                FROM read_parquet(?)
                """,
                [source, label, str(quarantine)],
            ).df()
            rejected_frames.append(rejected)

        first_bronze = data / "bronze" / "customers.parquet"
        run_id, ingested_at = connection.execute(
            "SELECT max(_run_id), max(_ingested_at_utc) FROM read_parquet(?)",
            [str(first_bronze)],
        ).fetchone()

    sources = pd.DataFrame(rows)
    rejected = pd.concat(rejected_frames, ignore_index=True)
    reasons = (
        rejected.assign(
            rule_code=rejected["rule_code"].str.split("|"),
            reason=rejected["reason"].str.split("|"),
        )
        .explode(["rule_code", "reason"])
        .groupby(["rule_code", "reason"], as_index=False)
        .size()
        .rename(columns={"size": "failures"})
        .sort_values(["failures", "rule_code"], ascending=[False, True])
    )
    received = int(sources["received"].sum())
    accepted = int(sources["accepted"].sum())
    quarantined = int(sources["quarantined"].sum())
    return QualitySnapshot(
        sources=sources,
        reasons=reasons,
        rejected=rejected,
        received=received,
        accepted=accepted,
        quarantined=quarantined,
        acceptance_rate=100 * accepted / received if received else 0.0,
        reconciled=bool(sources["reconciled"].all()),
        run_id=str(run_id),
        ingested_at=str(ingested_at),
    )
