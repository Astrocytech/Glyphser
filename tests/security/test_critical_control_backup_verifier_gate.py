from __future__ import annotations

import json
from pathlib import Path

from tooling.security import critical_control_backup_verifier_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _policy() -> dict[str, object]:
    return {
        "controls": [
            {
                "control_id": "policy_signature_verification",
                "primary_report": "policy_signature_gate.json",
                "backup_reports": ["security_verification_summary.json"],
                "fail_closed": True,
            }
        ]
    }


def test_backup_verifier_gate_passes_when_primary_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(sec / "policy_signature_gate.json", {"status": "PASS"})
    _write(gov / "critical_control_backup_policy.json", _policy())
    monkeypatch.setattr(critical_control_backup_verifier_gate, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_backup_verifier_gate,
        "POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_backup_verifier_gate, "evidence_root", lambda: repo / "evidence")
    assert critical_control_backup_verifier_gate.main([]) == 0


def test_backup_verifier_gate_uses_backup_when_primary_unavailable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(sec / "security_verification_summary.json", {"status": "PASS"})
    _write(gov / "critical_control_backup_policy.json", _policy())
    monkeypatch.setattr(critical_control_backup_verifier_gate, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_backup_verifier_gate,
        "POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_backup_verifier_gate, "evidence_root", lambda: repo / "evidence")
    assert critical_control_backup_verifier_gate.main([]) == 0
    report = json.loads((sec / "critical_control_backup_verifier_gate.json").read_text(encoding="utf-8"))
    assert "backup_verifier_used:policy_signature_verification:security_verification_summary.json" in report["findings"]


def test_backup_verifier_gate_fails_closed_when_primary_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(sec / "policy_signature_gate.json", {"status": "FAIL"})
    _write(sec / "security_verification_summary.json", {"status": "PASS"})
    _write(gov / "critical_control_backup_policy.json", _policy())
    monkeypatch.setattr(critical_control_backup_verifier_gate, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_backup_verifier_gate,
        "POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_backup_verifier_gate, "evidence_root", lambda: repo / "evidence")
    assert critical_control_backup_verifier_gate.main([]) == 1
    report = json.loads((sec / "critical_control_backup_verifier_gate.json").read_text(encoding="utf-8"))
    assert "primary_failed_fail_closed:policy_signature_verification:policy_signature_gate.json" in report["findings"]


def test_backup_verifier_gate_fails_when_control_unavailable_and_no_backup(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    _write(gov / "critical_control_backup_policy.json", _policy())
    monkeypatch.setattr(critical_control_backup_verifier_gate, "ROOT", repo)
    monkeypatch.setattr(
        critical_control_backup_verifier_gate,
        "POLICY",
        gov / "critical_control_backup_policy.json",
    )
    monkeypatch.setattr(critical_control_backup_verifier_gate, "evidence_root", lambda: repo / "evidence")
    assert critical_control_backup_verifier_gate.main([]) == 1
    report = json.loads((sec / "critical_control_backup_verifier_gate.json").read_text(encoding="utf-8"))
    assert "control_unavailable_no_backup:policy_signature_verification:policy_signature_gate.json" in report["findings"]
