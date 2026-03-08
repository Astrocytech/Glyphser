from __future__ import annotations

import json
from pathlib import Path

from tooling.security import required_control_condition_bypass_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_required_control_condition_bypass_gate_passes_when_controls_are_unconditional(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    wf_root = repo / ".github" / "workflows"
    wf = """
jobs:
  security:
    steps:
      - name: Policy signature
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
    _write(wf_root / "ci.yml", wf)
    _write(wf_root / "security-maintenance.yml", wf)
    _write(wf_root / "release.yml", wf)

    monkeypatch.setattr(required_control_condition_bypass_gate, "ROOT", repo)
    monkeypatch.setattr(required_control_condition_bypass_gate, "evidence_root", lambda: repo / "evidence")
    assert required_control_condition_bypass_gate.main([]) == 0


def test_required_control_condition_bypass_gate_fails_when_critical_control_is_conditional(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    wf_root = repo / ".github" / "workflows"
    conditional_wf = """
jobs:
  security:
    steps:
      - name: Policy signature
        if: github.ref == 'refs/heads/main'
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
    _write(wf_root / "ci.yml", conditional_wf)
    _write(wf_root / "security-maintenance.yml", conditional_wf)
    _write(wf_root / "release.yml", conditional_wf)

    monkeypatch.setattr(required_control_condition_bypass_gate, "ROOT", repo)
    monkeypatch.setattr(required_control_condition_bypass_gate, "evidence_root", lambda: repo / "evidence")
    assert required_control_condition_bypass_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "required_control_condition_bypass_gate.json").read_text("utf-8"))
    assert any(str(item).startswith("conditional_critical_control:") for item in report["findings"])
