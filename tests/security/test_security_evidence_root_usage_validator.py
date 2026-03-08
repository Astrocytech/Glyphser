from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_evidence_root_usage_validator


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_evidence_root_usage_validator_passes_when_env_var_used(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "run: python tooling/security/foo_gate.py\n"
        "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/foo.json\n",
    )

    monkeypatch.setattr(security_evidence_root_usage_validator, "ROOT", repo)
    monkeypatch.setattr(security_evidence_root_usage_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_evidence_root_usage_validator, "evidence_root", lambda: repo / "evidence")
    assert security_evidence_root_usage_validator.main([]) == 0


def test_security_evidence_root_usage_validator_fails_on_missing_env_or_hardcoded_path(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "run: python tooling/security/foo_gate.py\n"
        "path: evidence/security/foo.json\n",
    )

    monkeypatch.setattr(security_evidence_root_usage_validator, "ROOT", repo)
    monkeypatch.setattr(security_evidence_root_usage_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_evidence_root_usage_validator, "evidence_root", lambda: repo / "evidence")
    assert security_evidence_root_usage_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_evidence_root_usage_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_evidence_root_env_usage:") for item in report["findings"])
    assert any(item.startswith("hardcoded_evidence_security_path:") for item in report["findings"])
