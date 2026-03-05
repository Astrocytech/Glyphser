from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "tooling" / "security" / "templates"


def test_security_gate_template_prewires_report_contract() -> None:
    text = (TEMPLATES_DIR / "security_gate_template.py.tmpl").read_text(encoding="utf-8")
    assert '"status": "PASS" if not findings else "FAIL"' in text
    assert '"findings": findings' in text
    assert '"summary": {' in text
    assert '"metadata": {' in text
    assert "write_json_report" in text


def test_security_gate_test_template_prewires_test_hooks() -> None:
    text = (TEMPLATES_DIR / "security_gate_test_template.py.tmpl").read_text(encoding="utf-8")
    assert "def test_" in text
    assert "passes" in text
    assert "fails" in text
    assert '"status" in report and "findings" in report and "summary" in report and "metadata" in report' in text


def test_security_workflow_template_prewires_security_defaults() -> None:
    text = (TEMPLATES_DIR / "security_workflow_template.yml.tmpl").read_text(encoding="utf-8")
    assert "security-events: write" in text
    assert "TZ: \"UTC\"" in text
    assert "python tooling/security/install_security_toolchain.py" in text
    assert "semgrep --version" in text
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in text
    assert "actions/upload-artifact@" in text
