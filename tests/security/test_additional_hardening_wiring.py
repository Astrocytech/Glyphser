from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_new_security_workflows_exist_and_are_wired() -> None:
    for wf in [
        ROOT / ".github" / "workflows" / "security-baseline-update.yml",
        ROOT / ".github" / "workflows" / "security-audit-archive.yml",
        ROOT / ".github" / "workflows" / "emergency-lockdown.yml",
        ROOT / ".github" / "workflows" / "security-tamper-canary.yml",
        ROOT / ".github" / "workflows" / "security-compromised-runner-drill.yml",
        ROOT / ".github" / "workflows" / "security-replay-abuse-regression.yml",
        ROOT / ".github" / "workflows" / "security-control-recertification.yml",
    ]:
        text = wf.read_text(encoding="utf-8")
        assert "evidence_run_dir_guard.py" in text
    audit = (ROOT / ".github" / "workflows" / "security-audit-archive.yml").read_text(encoding="utf-8")
    assert "audit-log-archive.tar.gz.sha256" in audit
    assert "python tooling/security/long_term_retention_manifest.py" in audit
    assert "long_term_retention_manifest.json" in audit


def test_replay_abuse_regression_workflow_runs_multi_python_matrix() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-replay-abuse-regression.yml").read_text(encoding="utf-8")
    assert "matrix:" in wf
    assert 'python-version: ["3.11", "3.12"]' in wf
    assert "replay_abuse_regression_gate.py" in wf


def test_codeowners_and_review_policy_present() -> None:
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "/tooling/security/" in codeowners
    assert "/governance/security/" in codeowners
    assert "/.github/workflows/" in codeowners
