from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_stale_item_gate


def test_hardening_todo_stale_item_gate_detects_stale_items(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] item updated: 2020-01-01\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_stale_item_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_stale_item_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    monkeypatch.setenv("GLYPHSER_HARDENING_ITEM_SLA_DAYS", "30")
    assert hardening_todo_stale_item_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_stale_item_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(x).startswith("stale_item:") for x in report["findings"])


def test_hardening_todo_stale_item_gate_requires_updated_tag_when_enabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[~] in progress no timestamp\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_stale_item_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_stale_item_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_REQUIRE_UPDATED_TAG", "true")
    assert hardening_todo_stale_item_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_stale_item_gate.json").read_text(encoding="utf-8"))
    assert report["summary"]["missing_updated_tags"] == 1


def test_hardening_todo_stale_item_gate_uses_sla_policy_defaults(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] stale item updated: 2025-01-01\n", encoding="utf-8")
    policy = repo / "governance" / "security" / "hardening_backlog_sla_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps({"todo_path": "todo.txt", "sla_days": 30, "require_updated_tag": True}, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(hardening_todo_stale_item_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_stale_item_gate, "SLA_POLICY", policy)
    monkeypatch.setattr(hardening_todo_stale_item_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    monkeypatch.delenv("GLYPHSER_HARDENING_TODO_PATH", raising=False)
    monkeypatch.delenv("GLYPHSER_HARDENING_ITEM_SLA_DAYS", raising=False)
    monkeypatch.delenv("GLYPHSER_HARDENING_REQUIRE_UPDATED_TAG", raising=False)
    assert hardening_todo_stale_item_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_stale_item_gate.json").read_text(encoding="utf-8"))
    assert report["summary"]["sla_days"] == 30
    assert report["summary"]["require_updated_tag"] is True
