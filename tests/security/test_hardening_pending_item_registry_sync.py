from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_pending_item_registry_sync


def test_hardening_pending_item_registry_sync_assigns_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A. Alpha\n[ ] first\n[ ] second\n", encoding="utf-8")

    monkeypatch.setattr(hardening_pending_item_registry_sync, "ROOT", repo)
    monkeypatch.setattr(hardening_pending_item_registry_sync, "TODO", todo)
    monkeypatch.setattr(
        hardening_pending_item_registry_sync,
        "REGISTRY",
        repo / "governance" / "security" / "hardening_pending_item_registry.json",
    )
    monkeypatch.setattr(hardening_pending_item_registry_sync, "evidence_root", lambda: repo / "evidence")

    assert hardening_pending_item_registry_sync.main([]) == 0
    payload = json.loads((repo / "governance" / "security" / "hardening_pending_item_registry.json").read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in payload["entries"]]
    assert len(ids) == 2
    assert len(set(ids)) == 2
