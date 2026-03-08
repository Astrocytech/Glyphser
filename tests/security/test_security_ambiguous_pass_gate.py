from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_ambiguous_pass_gate


def test_security_ambiguous_pass_gate_passes_without_masking(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "security.yml").write_text(
        "jobs:\n  s:\n    steps:\n      - run: python tooling/security/security_super_gate.py --strict-key\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_ambiguous_pass_gate, "ROOT", repo)
    monkeypatch.setattr(security_ambiguous_pass_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_ambiguous_pass_gate, "evidence_root", lambda: repo / "evidence")
    assert security_ambiguous_pass_gate.main([]) == 0


def test_security_ambiguous_pass_gate_fails_with_masking(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "security.yml").write_text(
        "jobs:\n  s:\n    steps:\n      - run: python tooling/security/security_super_gate.py --strict-key || true\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_ambiguous_pass_gate, "ROOT", repo)
    monkeypatch.setattr(security_ambiguous_pass_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_ambiguous_pass_gate, "evidence_root", lambda: repo / "evidence")
    assert security_ambiguous_pass_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_ambiguous_pass_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("ambiguous_pass_pattern:") for item in report["findings"])
