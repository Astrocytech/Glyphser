from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_penetration_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-penetration.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "python -m pytest -q tests/security/test_penetration_scenarios.py" in wf
    assert "security-penetration-evidence" in wf
