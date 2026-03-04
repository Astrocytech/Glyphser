from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_tamper_e2e_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-tamper-e2e.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in wf
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in wf
    assert "python tooling/security/security_artifacts.py" in wf
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in wf
    assert 'echo "tampered" >>' in wf
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in wf
    assert "expected evidence_attestation_gate to fail on tampered evidence" in wf
