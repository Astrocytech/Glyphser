from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_pending_count_validator


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_hardening_pending_count_validator_passes_without_done_marker(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[ ] pending\n")
    monkeypatch.setattr(hardening_pending_count_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_pending_count_validator, "TODO", todo)
    monkeypatch.setattr(hardening_pending_count_validator, "evidence_root", lambda: repo / "evidence")
    assert hardening_pending_count_validator.main([]) == 0


def test_hardening_pending_count_validator_fails_when_done_with_unchecked(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[ ] pending\nDONE\n")
    monkeypatch.setattr(hardening_pending_count_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_pending_count_validator, "TODO", todo)
    monkeypatch.setattr(hardening_pending_count_validator, "evidence_root", lambda: repo / "evidence")
    assert hardening_pending_count_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_pending_count_validator.json").read_text(encoding="utf-8"))
    assert "done_marker_present_with_unchecked_items" in report["findings"]
