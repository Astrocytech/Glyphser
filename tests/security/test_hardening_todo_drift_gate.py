from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_todo_drift_gate


def test_hardening_todo_drift_gate_reports_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "foo_bar_gate.py").write_text("# gate\n", encoding="utf-8")
    todo = repo / "todo.txt"
    todo.write_text(
        "\n".join(
            [
                "[ ] Add foo bar gate",
                "[x] Add missing impl gate",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(hardening_todo_drift_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_drift_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_DRIFT_STRICT", "true")
    assert hardening_todo_drift_gate.main([]) == 1
    report = json.loads((ev / "hardening_todo_drift_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["summary"]["implemented_but_unchecked"] == 1
    assert report["summary"]["checked_but_missing_implementation"] == 1


def test_hardening_todo_drift_gate_passes_when_not_strict(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "foo_bar_gate.py").write_text("# gate\n", encoding="utf-8")
    todo = repo / "todo.txt"
    todo.write_text("[ ] Add foo bar gate\n", encoding="utf-8")
    monkeypatch.setattr(hardening_todo_drift_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_todo_drift_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TODO_PATH", str(todo))
    monkeypatch.delenv("GLYPHSER_HARDENING_TODO_DRIFT_STRICT", raising=False)
    assert hardening_todo_drift_gate.main([]) == 0
