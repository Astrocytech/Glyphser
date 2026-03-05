from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_overlap_redundancy_report


def test_hardening_overlap_redundancy_report_detects_cross_section_duplicates(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    repo.mkdir(parents=True, exist_ok=True)
    todo.write_text(
        "A. Alpha\n[x] Add immutable evidence index.\nB. Beta\n[ ] Add immutable evidence index.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(hardening_overlap_redundancy_report, "ROOT", repo)
    monkeypatch.setattr(hardening_overlap_redundancy_report, "TODO_PATH", todo)
    monkeypatch.setattr(hardening_overlap_redundancy_report, "evidence_root", lambda: repo / "evidence")
    assert hardening_overlap_redundancy_report.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_overlap_redundancy_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["overlap_groups"] == 1


def test_hardening_overlap_redundancy_report_handles_missing_todo(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(hardening_overlap_redundancy_report, "ROOT", repo)
    monkeypatch.setattr(hardening_overlap_redundancy_report, "TODO_PATH", repo / "missing.txt")
    monkeypatch.setattr(hardening_overlap_redundancy_report, "evidence_root", lambda: repo / "evidence")
    assert hardening_overlap_redundancy_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_overlap_redundancy_report.json").read_text(encoding="utf-8"))
    assert "missing_hardening_todo" in report["findings"]
