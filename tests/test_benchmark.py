import pytest

from fieldforge.cli import benchmark
from fieldforge.settings import ARTIFACTS_ROOT_ENV, DATA_ROOT_ENV


def test_benchmark_refuses_default_demo_roots(monkeypatch):
    monkeypatch.delenv(DATA_ROOT_ENV, raising=False)
    monkeypatch.delenv(ARTIFACTS_ROOT_ENV, raising=False)

    with pytest.raises(SystemExit, match="Benchmark roots must be relocated"):
        benchmark(profile="1x", seed=20260907, customers=500)
