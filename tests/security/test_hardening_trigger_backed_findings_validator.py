from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_trigger_backed_findings_validator


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_trigger_backed_findings_validator_passes_without_candidates(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    triage = repo / "evidence" / "security" / "weekly_hardening_triage.json"
    _write_json(triage, {"candidates": []})

    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "WEEKLY_TRIAGE", triage)
    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "evidence_root", lambda: repo / "evidence")
    assert hardening_trigger_backed_findings_validator.main([]) == 0


def test_hardening_trigger_backed_findings_validator_fails_with_candidates(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    triage = repo / "evidence" / "security" / "weekly_hardening_triage.json"
    _write_json(triage, {"candidates": [{"source": "incident:123"}]})

    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "WEEKLY_TRIAGE", triage)
    monkeypatch.setattr(hardening_trigger_backed_findings_validator, "evidence_root", lambda: repo / "evidence")
    assert hardening_trigger_backed_findings_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_trigger_backed_findings_validator.json").read_text(encoding="utf-8"))
    assert "unresolved_trigger_backed_findings:1" in report["findings"]
