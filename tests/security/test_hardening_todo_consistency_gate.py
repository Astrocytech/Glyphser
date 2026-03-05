from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_consistency_gate


def test_hardening_todo_consistency_gate_skips_when_file_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(repo / "missing.txt"))
    assert hardening_todo_consistency_gate.main([]) == 0


def test_hardening_todo_consistency_gate_fails_on_done_with_pending(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] pending\nDONE\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    assert hardening_todo_consistency_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_consistency_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "done_marker_present_with_pending_items" in report["findings"]
    assert report["summary"]["section_counts"]["GLOBAL"]["pending"] >= 1


def test_hardening_todo_consistency_gate_requires_trigger_references(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] pending without context\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_REQUIRE_TRIGGER_REF", "true")
    assert hardening_todo_consistency_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_consistency_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "pending_item_missing_trigger_reference" in report["findings"]
    assert report["summary"]["pending_without_trigger_reference"] == 1


def test_hardening_todo_consistency_gate_requires_owner_and_milestone_for_in_progress(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[~] in progress item\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_REQUIRE_OWNER_MILESTONE", "true")
    assert hardening_todo_consistency_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_consistency_gate.json").read_text(encoding="utf-8"))
    assert "in_progress_item_missing_owner" in report["findings"]
    assert "in_progress_item_missing_milestone" in report["findings"]


def test_hardening_todo_consistency_gate_requires_risk_acceptance_for_deferred(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] deferred until later\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_REQUIRE_RISK_ACCEPTANCE", "true")
    assert hardening_todo_consistency_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_consistency_gate.json").read_text(encoding="utf-8"))
    assert "deferred_item_missing_risk_acceptance" in report["findings"]


def test_hardening_todo_consistency_gate_requires_evidence_link_for_done(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[x] completed item\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_REQUIRE_DONE_EVIDENCE_LINK", "true")
    assert hardening_todo_consistency_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_consistency_gate.json").read_text(encoding="utf-8"))
    assert "done_item_missing_evidence_link" in report["findings"]
