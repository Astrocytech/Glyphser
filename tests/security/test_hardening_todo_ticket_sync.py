from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_ticket_sync


def test_hardening_todo_ticket_sync_detects_missing_ticket_and_owner(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] item without mapping\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_ticket_sync, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_ticket_sync, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    assert hardening_todo_ticket_sync.main([]) == 1
    report = json.loads((ev / "hardening_todo_ticket_sync.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "todo_items_missing_ticket_id:1" in report["findings"]
    assert "todo_items_missing_owner:1" in report["findings"]


def test_hardening_todo_ticket_sync_detects_state_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    states = repo / "tickets.json"
    todo.write_text("[ ] open item owner:sec ticket:SEC-123\n", encoding="utf-8")
    states.write_text(json.dumps({"SEC-123": "DONE"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_ticket_sync, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_ticket_sync, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    assert hardening_todo_ticket_sync.main(["--ticket-state-file", str(states)]) == 1
    report = json.loads((ev / "hardening_todo_ticket_sync.json").read_text(encoding="utf-8"))
    assert report["summary"]["todo_ticket_state_drift"] == 1
