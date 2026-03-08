from __future__ import annotations

import json
from pathlib import Path

from tooling.security import critical_control_redundancy_report


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_critical_control_redundancy_report_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(
        gov / "security_gate_dependency_policy.json",
        {
            "critical_controls": [
                {
                    "control_id": "c1",
                    "verifiers": ["gate_a", "gate_b"],
                    "required_redundant_verifiers": 2,
                }
            ]
        },
    )
    _write(
        gov / "critical_control_backup_policy.json",
        {
            "controls": [
                {
                    "control_id": "c1",
                    "primary_report": "gate_a",
                    "backup_reports": ["gate_b"],
                }
            ]
        },
    )
    monkeypatch.setattr(critical_control_redundancy_report, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_redundancy_report,
        "DEPENDENCY_POLICY",
        gov / "security_gate_dependency_policy.json",
    )
    monkeypatch.setattr(
        critical_control_redundancy_report,
        "BACKUP_POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_redundancy_report, "evidence_root", lambda: repo / "evidence")
    assert critical_control_redundancy_report.main([]) == 0


def test_critical_control_redundancy_report_fails_when_control_is_spof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(
        gov / "security_gate_dependency_policy.json",
        {
            "critical_controls": [
                {
                    "control_id": "c1",
                    "verifiers": ["gate_a"],
                    "required_redundant_verifiers": 2,
                }
            ]
        },
    )
    _write(
        gov / "critical_control_backup_policy.json",
        {
            "controls": [
                {
                    "control_id": "c1",
                    "primary_report": "gate_a",
                    "backup_reports": [],
                }
            ]
        },
    )
    monkeypatch.setattr(critical_control_redundancy_report, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_redundancy_report,
        "DEPENDENCY_POLICY",
        gov / "security_gate_dependency_policy.json",
    )
    monkeypatch.setattr(
        critical_control_redundancy_report,
        "BACKUP_POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_redundancy_report, "evidence_root", lambda: repo / "evidence")
    assert critical_control_redundancy_report.main([]) == 1
    payload = json.loads((sec / "critical_control_redundancy_report.json").read_text(encoding="utf-8"))
    assert "insufficient_redundancy:c1:1<2" in payload["findings"]
