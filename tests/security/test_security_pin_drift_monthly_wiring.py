from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_pin_drift_monthly_workflow_is_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-pin-drift-monthly.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "concurrency:" in wf
    assert "cancel-in-progress: false" in wf
    assert "python tooling/security/workflow_pin_drift_report.py" in wf
    assert "python tooling/security/security_dashboard_export.py" in wf
    assert "python tooling/security/monthly_security_program_health_report.py" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-pin-drift-monthly" in wf
    assert "monthly_security_program_health_report.json" in wf
    assert "monthly_security_program_health_report.json.sig" in wf
    assert "retention-days: 90" in wf
