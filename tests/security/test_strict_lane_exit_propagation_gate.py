from __future__ import annotations

import json
from pathlib import Path

from tooling.security import strict_lane_exit_propagation_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _workflow(mask: str = "") -> str:
    suffix = f" {mask}" if mask else ""
    return f"""
jobs:
  security:
    steps:
      - name: Policy signature
        run: python tooling/security/policy_signature_gate.py --strict-key{suffix}
      - name: Provenance signature
        run: python tooling/security/provenance_signature_gate.py --strict-key
      - name: Evidence attestation
        run: python tooling/security/evidence_attestation_gate.py --strict-key
      - name: Security super gate
        run: python tooling/security/security_super_gate.py --strict-key
"""


def test_strict_lane_exit_propagation_gate_passes_without_masking(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    _write(wf / "ci.yml", _workflow())
    _write(wf / "security-maintenance.yml", _workflow())
    _write(wf / "release.yml", _workflow())
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "ROOT", repo)
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "evidence_root", lambda: repo / "evidence")
    assert strict_lane_exit_propagation_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "strict_lane_exit_propagation_gate.json").read_text("utf-8"))
    assert report["status"] == "PASS"


def test_strict_lane_exit_propagation_gate_fails_on_shell_masking(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    _write(wf / "ci.yml", _workflow("|| true"))
    _write(wf / "security-maintenance.yml", _workflow())
    _write(wf / "release.yml", _workflow())
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "ROOT", repo)
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "evidence_root", lambda: repo / "evidence")
    assert strict_lane_exit_propagation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "strict_lane_exit_propagation_gate.json").read_text("utf-8"))
    assert any(str(item).startswith("critical_exit_masked_shell:") for item in report["findings"])


def test_strict_lane_exit_propagation_gate_fails_on_continue_on_error(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    _write(
        wf / "ci.yml",
        """
jobs:
  security:
    steps:
      - name: Policy signature
        continue-on-error: true
        run: python tooling/security/policy_signature_gate.py --strict-key
""",
    )
    _write(wf / "security-maintenance.yml", _workflow())
    _write(wf / "release.yml", _workflow())
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "ROOT", repo)
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "evidence_root", lambda: repo / "evidence")
    assert strict_lane_exit_propagation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "strict_lane_exit_propagation_gate.json").read_text("utf-8"))
    assert any(str(item).startswith("critical_exit_masked_continue_on_error:") for item in report["findings"])


def test_strict_lane_exit_propagation_gate_detects_variant_invocation_masking(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    _write(
        wf / "ci.yml",
        """
jobs:
  security:
    steps:
      - name: Policy signature variant
        continue-on-error: true
        run: python3 tooling/security/policy_signature_gate.py --strict-key --profile ci
""",
    )
    _write(wf / "security-maintenance.yml", _workflow())
    _write(wf / "release.yml", _workflow())
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "ROOT", repo)
    monkeypatch.setattr(strict_lane_exit_propagation_gate, "evidence_root", lambda: repo / "evidence")
    assert strict_lane_exit_propagation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "strict_lane_exit_propagation_gate.json").read_text("utf-8"))
    assert any(
        item == "critical_exit_masked_continue_on_error:.github/workflows/ci.yml:5:tooling/security/policy_signature_gate.py"
        for item in report["findings"]
    )
