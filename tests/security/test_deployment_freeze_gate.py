from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deployment_freeze_gate


def test_deployment_freeze_gate_passes_when_critical_reports_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in ["security_super_gate.json", "policy_signature.json"]:
        (sec / name).write_text('{"status":"PASS"}\n', encoding="utf-8")
    monkeypatch.setattr(deployment_freeze_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        deployment_freeze_gate,
        "load_policy",
        lambda: {"enforce_deployment_freeze": True, "critical_freeze_reports": ["security_super_gate.json", "policy_signature.json"]},
    )
    assert deployment_freeze_gate.main([]) == 0


def test_deployment_freeze_gate_fails_when_critical_report_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "security_super_gate.json").write_text('{"status":"FAIL"}\n', encoding="utf-8")
    monkeypatch.setattr(deployment_freeze_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        deployment_freeze_gate,
        "load_policy",
        lambda: {"enforce_deployment_freeze": True, "critical_freeze_reports": ["security_super_gate.json"]},
    )
    assert deployment_freeze_gate.main([]) == 1
