from pathlib import Path

import duckdb
import pytest

from dashboard import warehouse


def test_load_query_frames_executes_named_queries(tmp_path: Path):
    database = tmp_path / "warehouse.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("create table sample as select 3 as accepted")

    frames = warehouse.load_query_frames(
        database,
        {
            "count": "select count(*) as rows from sample",
            "value": "select accepted from sample",
        },
    )

    assert frames["count"].iloc[0].to_dict() == {"rows": 1}
    assert frames["value"].iloc[0].to_dict() == {"accepted": 3}


def test_load_query_frames_classifies_lock_as_transient(monkeypatch, tmp_path: Path):
    def locked_connect(*args, **kwargs):
        raise duckdb.IOException("Could not set lock on file")

    monkeypatch.setattr(warehouse.duckdb, "connect", locked_connect)

    with pytest.raises(warehouse.WarehouseBusyError):
        warehouse.load_query_frames(tmp_path / "warehouse.duckdb", {"one": "select 1"})


def test_load_query_frames_preserves_unrelated_io_errors(monkeypatch, tmp_path: Path):
    def broken_connect(*args, **kwargs):
        raise duckdb.IOException("filesystem read failed")

    monkeypatch.setattr(warehouse.duckdb, "connect", broken_connect)

    with pytest.raises(duckdb.IOException, match="filesystem read failed"):
        warehouse.load_query_frames(tmp_path / "warehouse.duckdb", {"one": "select 1"})
