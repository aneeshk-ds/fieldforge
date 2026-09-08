"""Path resolution for FieldForge.

Paths resolve when they are called, not when this module is imported, so a
caller can point the whole pipeline at an isolated location by setting
FIELDFORGE_DATA_ROOT and FIELDFORGE_ARTIFACTS_ROOT. Tests use that to run the
generation and validation stages without touching the demo run in data/.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = 20260907
DATA_ROOT_ENV = "FIELDFORGE_DATA_ROOT"
ARTIFACTS_ROOT_ENV = "FIELDFORGE_ARTIFACTS_ROOT"


def data_root() -> Path:
    """Directory holding source, bronze, silver, quarantine, gold and the warehouse."""
    return Path(os.environ.get(DATA_ROOT_ENV) or ROOT / "data")


def artifacts_root() -> Path:
    """Directory holding profiling, validation, reconciliation and manifest evidence."""
    return Path(os.environ.get(ARTIFACTS_ROOT_ENV) or ROOT / "artifacts")


def source_dir() -> Path:
    return data_root() / "source"


def bronze_dir() -> Path:
    return data_root() / "bronze"


def silver_dir() -> Path:
    return data_root() / "silver"


def quarantine_dir() -> Path:
    return data_root() / "quarantine"


def gold_dir() -> Path:
    return data_root() / "gold"


def warehouse_path() -> Path:
    return data_root() / "fieldforge.duckdb"


def is_isolated() -> bool:
    """True when either root has been redirected away from the repository."""
    return bool(os.environ.get(DATA_ROOT_ENV) or os.environ.get(ARTIFACTS_ROOT_ENV))


def ensure_directories() -> None:
    for path in (
        source_dir(),
        bronze_dir(),
        silver_dir(),
        quarantine_dir(),
        gold_dir(),
        artifacts_root(),
    ):
        path.mkdir(parents=True, exist_ok=True)
