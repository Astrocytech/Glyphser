from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_debt_report


def test_hardening_todo_debt_report_passes_and_summarizes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("A. Area\n[ ] one\n[~] two\n[x] three\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_debt_report, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_debt_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    assert hardening_todo_debt_report.main([]) == 0
    report = json.loads((ev / "hardening_todo_debt_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["total_pending"] == 1
    assert report["summary"]["total_in_progress"] == 1
    assert report["summary"]["total_done"] == 1


def test_hardening_todo_debt_report_fails_when_pending_budget_exceeded(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] a\n[ ] b\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_debt_report, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_debt_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_MAX_PENDING", "1")
    assert hardening_todo_debt_report.main([]) == 1
    report = json.loads((ev / "hardening_todo_debt_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(x).startswith("pending_budget_exceeded:") for x in report["findings"])
