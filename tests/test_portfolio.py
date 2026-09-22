from pathlib import Path

import pytest

from fieldforge.portfolio import PortfolioCheckError, load_tool_inventory, portfolio_check
from fieldforge.settings import ROOT


def test_portfolio_inventory_evidences_all_39_tools():
    result = portfolio_check(write_receipt=False)

    assert result["status"] == "passed"
    assert result["tool_count"] == 39
    assert result["tool_ids_complete"]


def test_tool_inventory_rejects_duplicate_or_missing_ids(tmp_path: Path):
    inventory = tmp_path / "tools.yml"
    inventory.write_text(
        "version: 1\ntools:\n  - id: 1\n    name: One\n    usage: long enough usage\n"
        "    evidence: [README.md]\n  - id: 1\n    name: Two\n"
        "    usage: another long usage\n    evidence: [README.md]\n",
        encoding="utf-8",
    )

    with pytest.raises(PortfolioCheckError, match="schema failed"):
        load_tool_inventory(inventory)


def test_portfolio_check_rejects_stale_active_branch_reference(tmp_path: Path):
    for relative in ("README.md", "CLAUDE.md", "docs/demo.md", "docs/tools-and-evidence.md", "docs/repository-knowledge.md"):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("claudework" if relative == "README.md" else "current", encoding="utf-8")
    for relative in set(("docs/architecture.md", "docs/acceptance-criteria.md", "docs/kpi-audit.md", "docs/resume-bullets.md")):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("current", encoding="utf-8")

    with pytest.raises(PortfolioCheckError, match="Portfolio check failed"):
        portfolio_check(root=tmp_path, inventory_path=ROOT / "config/tool_inventory.yml", write_receipt=False)
