from __future__ import annotations

import json
from pathlib import Path

from tooling.security import incident_regression_catalog_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_incident_regression_catalog_gate_passes_for_valid_catalog(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "incident_regression_catalog.json",
        {
            "schema_version": 1,
            "incidents": [
                {
                    "incident_id": "INC-1001",
                    "severity": "high",
                    "failing_controls": ["security_event_schema_gate"],
                    "regression_tests": ["tests/security/test_security_event_schema_gate.py::test_detects_missing_field"],
                }
            ],
        },
    )

    monkeypatch.setattr(incident_regression_catalog_gate, "ROOT", repo)
    monkeypatch.setattr(
        incident_regression_catalog_gate,
        "CATALOG",
        repo / "governance/security/incident_regression_catalog.json",
    )
    monkeypatch.setattr(incident_regression_catalog_gate, "evidence_root", lambda: repo / "evidence")
    assert incident_regression_catalog_gate.main([]) == 0


def test_incident_regression_catalog_gate_fails_on_missing_links(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "incident_regression_catalog.json",
        {
            "schema_version": 1,
            "incidents": [{"incident_id": "INC-1001", "failing_controls": [], "regression_tests": []}],
        },
    )

    monkeypatch.setattr(incident_regression_catalog_gate, "ROOT", repo)
    monkeypatch.setattr(
        incident_regression_catalog_gate,
        "CATALOG",
        repo / "governance/security/incident_regression_catalog.json",
    )
    monkeypatch.setattr(incident_regression_catalog_gate, "evidence_root", lambda: repo / "evidence")
    assert incident_regression_catalog_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "incident_regression_catalog_gate.json").read_text(encoding="utf-8"))
    assert "missing_failing_controls:1" in report["findings"]
    assert "missing_regression_tests:1" in report["findings"]
