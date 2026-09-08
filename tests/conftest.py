"""Shared fixtures.

Pipeline tests must never overwrite the demo run in the repository, so
isolated_data_root redirects both roots at a temporary directory for the module
that uses it. Evidence from a passing run is disposable. When a test fails, the
evidence JSON from that isolated run is copied to artifacts/test-runs/<run-id>/
with a failure report, so the run can be investigated without disturbing the
data the dashboard reads. artifacts/ is Git-ignored.
"""

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fieldforge import settings

TEST_RUN_DIR = "test-runs"
_failures: list[dict[str, str]] = []


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if report.when in {"setup", "call"} and report.failed:
        _failures.append(
            {
                "test": report.nodeid,
                "phase": report.when,
                "message": str(report.longrepr)[:4000],
            }
        )
    return report


@pytest.fixture(scope="session")
def test_run_id() -> str:
    """Unique, traceable run identifier stamped onto records ingested by tests."""
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    return f"test-{stamp}-{uuid.uuid4().hex[:8]}"


def _preserve_failed_run(isolated_root: Path, run_id: str) -> Path:
    destination = settings.ROOT / "artifacts" / TEST_RUN_DIR / run_id
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted((isolated_root / "artifacts").glob("*.json")):
        shutil.copy2(path, destination / path.name)
    report = {
        "run_id": run_id,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "isolated_data_root": str(isolated_root / "data"),
        "artifact_path": str(destination),
        "seed": settings.DEFAULT_SEED,
        "note": "Source records are regenerable from the seed; only evidence JSON is retained.",
        "failures": _failures,
    }
    (destination / "failure_report.json").write_text(json.dumps(report, indent=2))
    return destination


@pytest.fixture(scope="module")
def isolated_data_root(tmp_path_factory, test_run_id) -> Path:
    root = tmp_path_factory.mktemp("fieldforge-isolated")
    with pytest.MonkeyPatch.context() as patched:
        patched.setenv(settings.DATA_ROOT_ENV, str(root / "data"))
        patched.setenv(settings.ARTIFACTS_ROOT_ENV, str(root / "artifacts"))
        settings.ensure_directories()
        yield root
        if _failures:
            destination = _preserve_failed_run(root, test_run_id)
            print(f"\nTest run {test_run_id} failed. Evidence retained at {destination}")
