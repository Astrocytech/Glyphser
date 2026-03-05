from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_control_recertification_workflow_is_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-control-recertification.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "concurrency:" in wf
    assert "cancel-in-progress: false" in wf
    assert "python tooling/security/security_control_recertification.py" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-control-recertification" in wf
    assert "security_control_recertification.json" in wf
    assert "security_control_recertification.json.sig" in wf
