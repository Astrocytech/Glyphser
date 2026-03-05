from __future__ import annotations

import json
from pathlib import Path

from tooling.security import high_severity_incident_regression_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_high_severity_incident_regression_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "incident_regression_catalog.json",
        {
            "incidents": [
                {
                    "incident_id": "INC-1001",
                    "severity": "high",
                    "failing_controls": ["control-a"],
                    "regression_tests": ["tests/security/test_control_a.py::test_inc_1001"],
                }
            ]
        },
    )

    monkeypatch.setattr(high_severity_incident_regression_gate, "ROOT", repo)
    monkeypatch.setattr(
        high_severity_incident_regression_gate,
        "CATALOG",
        repo / "governance/security/incident_regression_catalog.json",
    )
    monkeypatch.setattr(high_severity_incident_regression_gate, "evidence_root", lambda: repo / "evidence")
    assert high_severity_incident_regression_gate.main([]) == 0


def test_high_severity_incident_regression_gate_fails_when_missing_permanent_test(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "incident_regression_catalog.json",
        {
            "incidents": [
                {
                    "incident_id": "INC-1001",
                    "severity": "high",
                    "failing_controls": ["control-a"],
                    "regression_tests": ["docs/incidents/inc-1001.md"],
                }
            ]
        },
    )

    monkeypatch.setattr(high_severity_incident_regression_gate, "ROOT", repo)
    monkeypatch.setattr(
        high_severity_incident_regression_gate,
        "CATALOG",
        repo / "governance/security/incident_regression_catalog.json",
    )
    monkeypatch.setattr(high_severity_incident_regression_gate, "evidence_root", lambda: repo / "evidence")
    assert high_severity_incident_regression_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "high_severity_incident_regression_gate.json").read_text(encoding="utf-8"))
    assert "high_severity_missing_permanent_test_reference:INC-1001" in report["findings"]
