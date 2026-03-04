from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_new_security_workflows_exist_and_are_wired() -> None:
    for wf in [
        ROOT / ".github" / "workflows" / "security-baseline-update.yml",
        ROOT / ".github" / "workflows" / "security-audit-archive.yml",
        ROOT / ".github" / "workflows" / "emergency-lockdown.yml",
        ROOT / ".github" / "workflows" / "security-tamper-canary.yml",
    ]:
        text = wf.read_text(encoding="utf-8")
        assert "evidence_run_dir_guard.py" in text


def test_codeowners_and_review_policy_present() -> None:
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "/tooling/security/" in codeowners
    assert "/governance/security/" in codeowners
    assert "/.github/workflows/" in codeowners
