from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_burndown_dashboard


def test_hardening_todo_burndown_dashboard_writes_history_and_dashboard(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] a\n[x] b\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_burndown_dashboard, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_burndown_dashboard, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert hardening_todo_burndown_dashboard.main([]) == 0

    dashboard = json.loads((ev / "hardening_burndown_dashboard.json").read_text(encoding="utf-8"))
    history_report = json.loads((ev / "hardening_burndown_history.json").read_text(encoding="utf-8"))
    assert dashboard["status"] == "PASS"
    assert dashboard["summary"]["current"]["pending"] == 1
    assert dashboard["summary"]["current"]["done"] == 1
    assert history_report["status"] == "PASS"
    assert history_report["summary"]["samples"] >= 1


def test_hardening_todo_burndown_dashboard_computes_delta(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    todo = repo / "todo.txt"
    todo.write_text("[ ] a\n[x] b\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_burndown_dashboard, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_burndown_dashboard, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert hardening_todo_burndown_dashboard.main([]) == 0

    todo.write_text("[x] a\n[x] b\n", encoding="utf-8")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-06T00:00:00+00:00")
    assert hardening_todo_burndown_dashboard.main([]) == 0
    dashboard = json.loads((ev / "hardening_burndown_dashboard.json").read_text(encoding="utf-8"))
    assert dashboard["summary"]["delta_pending_vs_prev"] == -1
    assert dashboard["summary"]["delta_done_vs_prev"] == 1
