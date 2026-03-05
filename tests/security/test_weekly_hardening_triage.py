from __future__ import annotations

import json
from pathlib import Path

from tooling.security import weekly_hardening_triage


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_weekly_hardening_triage_emits_only_trigger_backed_candidates(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    trigger_report = repo / "evidence" / "security" / "hardening_backlog_trigger_gate.json"
    _write_json(
        trigger_report,
        {
            "changed_sources": [
                {"path": "governance/security/incident_regression_catalog.json"},
                {"path": "governance/security/metadata/THREAT_MODEL.meta.json"},
            ]
        },
    )
    monkeypatch.setattr(weekly_hardening_triage, "ROOT", repo)
    monkeypatch.setattr(weekly_hardening_triage, "TRIGGER_GATE_REPORT", trigger_report)
    monkeypatch.setattr(weekly_hardening_triage, "evidence_root", lambda: repo / "evidence")
    assert weekly_hardening_triage.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "weekly_hardening_triage.json").read_text(encoding="utf-8"))
    assert report["summary"]["trigger_backed_candidates"] == 2
    assert report["summary"]["non_trigger_candidates"] == 0


def test_weekly_hardening_triage_fails_when_trigger_report_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(weekly_hardening_triage, "ROOT", repo)
    monkeypatch.setattr(weekly_hardening_triage, "TRIGGER_GATE_REPORT", repo / "missing.json")
    monkeypatch.setattr(weekly_hardening_triage, "evidence_root", lambda: repo / "evidence")
    assert weekly_hardening_triage.main([]) == 1
