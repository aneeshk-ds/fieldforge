"""Private-project acceptance progress derived from the release checklist."""

from pathlib import Path


def acceptance_progress(path: Path) -> tuple[int, int]:
    """Return completed and total private-prototype acceptance criteria."""
    checklist = [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().lower().startswith(("- [x]", "- [ ]"))
    ]
    if not checklist:
        raise ValueError(f"No acceptance criteria found in {path}")
    return sum(line.startswith("- [x]") for line in checklist), len(checklist)
