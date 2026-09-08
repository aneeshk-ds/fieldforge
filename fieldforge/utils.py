import hashlib
import json
from pathlib import Path

import pandas as pd


def stable_hash(*values: object) -> str:
    raw = "|".join("" if pd.isna(v) else str(v).strip().lower() for v in values)
    return hashlib.sha256(raw.encode()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def normalize_email(value: object) -> str | None:
    if pd.isna(value) or not str(value).strip():
        return None
    return str(value).strip().lower()


def normalize_phone(value: object) -> str | None:
    if pd.isna(value) or not str(value).strip():
        return None
    digits = "".join(c for c in str(value) if c.isdigit())
    return digits[-10:] if len(digits) >= 10 else None
