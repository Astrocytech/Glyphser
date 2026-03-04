from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_super_extended_workflow_is_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-super-extended.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "python tooling/security/security_super_gate.py --strict-key --strict-prereqs --include-extended" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-super-extended" in wf
    assert "semgrep==1.95.0" in wf
    assert "setuptools==75.8.0" in wf
    assert "semgrep --version" in wf
    assert 'python -c "import pkg_resources"' in wf
