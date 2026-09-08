from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE = DATA / "source"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
QUARANTINE = DATA / "quarantine"
GOLD = DATA / "gold"
ARTIFACTS = ROOT / "artifacts"
WAREHOUSE = DATA / "fieldforge.duckdb"
DEFAULT_SEED = 20260907


def ensure_directories() -> None:
    for path in (SOURCE, BRONZE, SILVER, QUARANTINE, GOLD, ARTIFACTS):
        path.mkdir(parents=True, exist_ok=True)
