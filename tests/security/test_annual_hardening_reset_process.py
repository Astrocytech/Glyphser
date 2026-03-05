from __future__ import annotations

import json
from pathlib import Path

from tooling.security import annual_hardening_reset_process


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_annual_hardening_reset_process_archives_completed_and_seeds_net_new(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.write_text(
        "A. Completed\n[x] done a\n[x] done b\nB. Active\n[x] done c\n[ ] pending d\n",
        encoding="utf-8",
    )
    _write_json(
        repo / "governance" / "security" / "adversarial_detection_history.json",
        {"events": [{"scenario_id": "new-scenario"}]},
    )
    _write_json(
        repo / "governance" / "security" / "incident_regression_catalog.json",
        {"incidents": []},
    )

    monkeypatch.setattr(annual_hardening_reset_process, "ROOT", repo)
    monkeypatch.setattr(annual_hardening_reset_process, "TODO_PATH", todo)
    monkeypatch.setattr(
        annual_hardening_reset_process,
        "ADVERSARIAL_HISTORY",
        repo / "governance" / "security" / "adversarial_detection_history.json",
    )
    monkeypatch.setattr(
        annual_hardening_reset_process,
        "INCIDENT_CATALOG",
        repo / "governance" / "security" / "incident_regression_catalog.json",
    )
    monkeypatch.setattr(annual_hardening_reset_process, "evidence_root", lambda: repo / "evidence")

    assert annual_hardening_reset_process.main([]) == 0
    archive = json.loads((repo / "evidence" / "security" / "annual_hardening_archive.json").read_text(encoding="utf-8"))
    seed = json.loads((repo / "evidence" / "security" / "annual_hardening_seed_risks.json").read_text(encoding="utf-8"))
    assert archive["summary"]["archived_sections"] == 1
    assert seed["summary"]["seeded_net_new_risks"] == 1


def test_annual_hardening_reset_process_fails_when_todo_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(annual_hardening_reset_process, "ROOT", repo)
    monkeypatch.setattr(annual_hardening_reset_process, "TODO_PATH", repo / "missing.txt")
    monkeypatch.setattr(annual_hardening_reset_process, "evidence_root", lambda: repo / "evidence")
    assert annual_hardening_reset_process.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "annual_hardening_reset_process.json").read_text(encoding="utf-8"))
    assert "missing_hardening_todo" in report["findings"]
