from __future__ import annotations

import json
from pathlib import Path

from tooling.security import control_failure_mode_remediation_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_control_failure_mode_remediation_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    baseline = repo / "governance" / "security" / "control_id_immutability_baseline.json"
    _write_json(
        matrix,
        {
            "controls": [
                {
                    "id": "CTRL-ONE",
                    "failure_mode": "Control bypassed by unsigned artifact.",
                    "expected_remediation": "Reject release, rotate signing key, and rerun attestations.",
                    "success_criterion": "All unsigned artifacts are rejected during promotion checks.",
                    "owner_escalation_path": "security-team -> oncall -> director",
                }
            ]
        },
    )
    _write_json(baseline, {"control_ids": ["CTRL-ONE"]})

    monkeypatch.setattr(control_failure_mode_remediation_gate, "ROOT", repo)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "MATRIX", matrix)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "IMMUTABILITY_BASELINE", baseline)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "evidence_root", lambda: repo / "evidence")

    assert control_failure_mode_remediation_gate.main([]) == 0


def test_control_failure_mode_remediation_gate_fails_on_missing_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    baseline = repo / "governance" / "security" / "control_id_immutability_baseline.json"
    _write_json(
        matrix,
        {
            "controls": [
                {
                    "id": "CTRL-ONE",
                    "failure_mode": "",
                    "expected_remediation": "",
                    "success_criterion": "",
                    "owner_escalation_path": "",
                }
            ]
        },
    )
    _write_json(baseline, {"control_ids": ["CTRL-ONE"]})

    monkeypatch.setattr(control_failure_mode_remediation_gate, "ROOT", repo)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "MATRIX", matrix)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "IMMUTABILITY_BASELINE", baseline)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "evidence_root", lambda: repo / "evidence")

    assert control_failure_mode_remediation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "control_failure_mode_remediation_gate.json").read_text(encoding="utf-8"))
    assert "missing_failure_mode:CTRL-ONE" in report["findings"]
    assert "missing_expected_remediation:CTRL-ONE" in report["findings"]
    assert "missing_success_criterion:CTRL-ONE" in report["findings"]
    assert "missing_owner_escalation_path:CTRL-ONE" in report["findings"]


def test_control_failure_mode_remediation_gate_fails_on_control_id_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    baseline = repo / "governance" / "security" / "control_id_immutability_baseline.json"
    _write_json(
        matrix,
        {
            "controls": [
                {
                    "id": "CTRL-NEW",
                    "failure_mode": "x",
                    "expected_remediation": "y",
                    "success_criterion": "z",
                    "owner_escalation_path": "security-team -> oncall",
                }
            ]
        },
    )
    _write_json(baseline, {"control_ids": ["CTRL-OLD"]})

    monkeypatch.setattr(control_failure_mode_remediation_gate, "ROOT", repo)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "MATRIX", matrix)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "IMMUTABILITY_BASELINE", baseline)
    monkeypatch.setattr(control_failure_mode_remediation_gate, "evidence_root", lambda: repo / "evidence")

    assert control_failure_mode_remediation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "control_failure_mode_remediation_gate.json").read_text(encoding="utf-8"))
    assert "control_id_added_without_baseline_update:CTRL-NEW" in report["findings"]
    assert "control_id_removed_without_baseline_update:CTRL-OLD" in report["findings"]
