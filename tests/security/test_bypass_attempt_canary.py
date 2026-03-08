from __future__ import annotations

import json
from pathlib import Path

from tooling.security import required_control_condition_bypass_gate, strict_lane_exit_propagation_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_bypass_attempt_canary_conditional_critical_control_hard_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    text = """
jobs:
  security:
    steps:
      - name: Policy signature
        if: always()
        run: python tooling/security/policy_signature_gate.py --strict-key
      - name: Provenance signature
        run: python tooling/security/provenance_signature_gate.py --strict-key
      - name: Evidence attestation
        run: python tooling/security/evidence_attestation_gate.py --strict-key
      - name: Security summary
        run: python tooling/security/security_verification_summary.py --strict-key
      - name: Security super gate
        run: python tooling/security/security_super_gate.py --strict-key
"""
    _write(wf / "ci.yml", text)
    _write(wf / "security-maintenance.yml", text)
    _write(wf / "release.yml", text)
    monkeypatch.setattr(required_control_condition_bypass_gate, "ROOT", repo)
    monkeypatch.setattr(required_control_condition_bypass_gate, "evidence_root", lambda: repo / "evidence")
    rc = required_control_condition_bypass_gate.main([])
    report = json.loads((repo / "evidence" / "security" / "required_control_condition_bypass_gate.json").read_text("utf-8"))
    assert rc == 1
    assert report["status"] == "FAIL"


def test_bypass_attempt_canary_shell_masking_hard_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    _write(
        wf / "ci.yml",
        """
jobs:
  security:
    steps:
      - name: Policy signature
        run: python tooling/security/policy_signature_gate.py --strict-key || true
""",
    )
    _write(
        wf / "security-maintenance.yml",
        """
jobs:
  security:
    steps:
      - name: Provenance signature
        run: python tooling/security/provenance_signature_gate.py --strict-key
      - name: Evidence attestation
        run: python tooling/security/evidence_attestation_gate.py --strict-key
      - name: Security super gate
        run: python tooling/security/security_super_gate.py --strict-key
""",
    )
    _write(wf / "release.yml", (wf / "security-maintenance.yml").read_text(encoding="utf-8"))
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "ROOT", repo)
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "evidence_root", lambda: repo / "evidence")
    rc = strict_lane_exit_propagation_gate.main([])
    report = json.loads((repo / "evidence" / "security" / "strict_lane_exit_propagation_gate.json").read_text("utf-8"))
    assert rc == 1
    assert report["status"] == "FAIL"
