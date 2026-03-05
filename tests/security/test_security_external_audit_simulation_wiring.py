from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_external_audit_simulation_workflow_is_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-external-audit-simulation.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "permissions:" in wf
    assert "contents: read" in wf
    assert "python tooling/security/external_audit_simulation.py --audit-id" in wf
    assert "external_audit_simulation.json" in wf
    assert "external_audit_simulation_closure.json" in wf
