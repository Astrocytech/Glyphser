from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_branch_protection_ops_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "branch-protection-ops.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in wf
    assert "python tooling/security/apply_branch_protection.py" in wf
    assert "python tooling/security/verify_branch_protection_live.py" in wf
    assert 'default: "owner/repo"' not in wf
    assert "BRANCH_PROTECTION_ADMIN_TOKEN" in wf


def test_security_live_integrations_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-live-integrations.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "python tooling/security/live_integrations_verify.py" in wf
    assert "live-integrations" in wf
    assert "GLYPHSER_WAF_HEALTH_URL" in wf
    assert "GLYPHSER_SIEM_HEALTH_URL" in wf
    assert "GLYPHSER_PAGING_HEALTH_URL" in wf
