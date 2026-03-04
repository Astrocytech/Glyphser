from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_maintenance_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-maintenance.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "python tooling/security/dependency_refresh_report.py" in wf
    assert "python tooling/security/pip_audit_gate.py" in wf
    assert "python tooling/security/secret_scan_gate.py" in wf
    assert "python tooling/security/workflow_pinning_gate.py" in wf
    assert "python tooling/security/incident_response_gate.py" in wf
    assert "python tooling/security/provenance_signature_gate.py" in wf
    assert "python tooling/security/slsa_attestation_gate.py" in wf
    assert "security-maintenance-artifacts" in wf
