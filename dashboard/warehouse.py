"""Read-only access helpers for the governed DuckDB warehouse."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import duckdb
import pandas as pd


class WarehouseBusyError(RuntimeError):
    """Raised when a pipeline rebuild temporarily owns the DuckDB file lock."""


def load_query_frames(
    database: Path, queries: Mapping[str, str]
) -> dict[str, pd.DataFrame]:
    """Execute a bounded set of read-only dashboard queries in one connection."""
    try:
        with duckdb.connect(str(database), read_only=True) as connection:
            return {name: connection.execute(sql).df() for name, sql in queries.items()}
    except duckdb.IOException as error:
        if "lock" in str(error).lower():
            raise WarehouseBusyError from error
        raise
