from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_conformance_workflow_security_coupling_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "conformance-gate.yml").read_text(encoding="utf-8")
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/conformance" in wf
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in wf
    assert "python tooling/security/policy_signature_gate.py --strict-key" in wf
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in wf
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in wf
    assert "python tooling/security/conformance_security_coupling_gate.py" in wf
