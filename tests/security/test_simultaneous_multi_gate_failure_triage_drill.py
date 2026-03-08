from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import simultaneous_multi_gate_failure_triage_drill


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_simultaneous_multi_gate_failure_triage_drill_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "simultaneous_multi_gate_failure_triage_drill.json"
    _write(
        drill,
        {
            "status": "PASS",
            "incident_id": "INC-1",
            "triage_started_at_utc": "2026-03-01T10:00:00+00:00",
            "triage_completed_at_utc": "2026-03-01T10:15:00+00:00",
            "failing_gates": ["gate-a", "gate-b"],
            "escalation_path": ["security-oncall"],
            "root_cause": "Synthetic drill case.",
            "remediation_actions": ["Action 1"],
        },
    )
    _sign(drill)

    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "ROOT", repo)
    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "DRILL", drill)
    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "evidence_root", lambda: repo / "evidence")
    assert simultaneous_multi_gate_failure_triage_drill.main([]) == 0


def test_simultaneous_multi_gate_failure_triage_drill_fails_on_invalid_payload(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "simultaneous_multi_gate_failure_triage_drill.json"
    _write(
        drill,
        {
            "status": "FAIL",
            "incident_id": "",
            "triage_started_at_utc": "bad",
            "triage_completed_at_utc": "bad",
            "failing_gates": ["only-one"],
            "escalation_path": [],
            "root_cause": "",
            "remediation_actions": [],
        },
    )
    _sign(drill)

    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "ROOT", repo)
    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "DRILL", drill)
    monkeypatch.setattr(simultaneous_multi_gate_failure_triage_drill, "evidence_root", lambda: repo / "evidence")
    assert simultaneous_multi_gate_failure_triage_drill.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "simultaneous_multi_gate_failure_triage_drill.json").read_text(
            encoding="utf-8"
        )
    )
    assert "insufficient_simultaneous_failures:1<2" in report["findings"]
    assert "invalid_triage_timestamps" in report["findings"]
