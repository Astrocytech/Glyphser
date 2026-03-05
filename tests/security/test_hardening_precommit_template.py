from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_hardening_precommit_template_contains_required_maintenance_commands() -> None:
    hook = (ROOT / ".githooks" / "pre-commit-hardening.sample").read_text(encoding="utf-8")
    assert "hardening_todo_index.py" in hook
    assert "hardening_pending_item_registry_sync.py" in hook
    assert "hardening_pending_count_validator.py" in hook
