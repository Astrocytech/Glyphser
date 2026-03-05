from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_env_injection_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_workflow_env_injection_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    _write(
        wf / "security.yml",
        "jobs:\n  a:\n    env:\n      GLYPHSER_ENV: ci\n      TZ: UTC\n",
    )
    _write(
        gov / "workflow_env_var_policy.json",
        json.dumps(
            {
                "workflow_file_globs": ["*.yml"],
                "allowed_env_var_patterns": ["^GLYPHSER_[A-Z0-9_]+$", "^TZ$"],
            }
        )
        + "\n",
    )
    monkeypatch.setattr(workflow_env_injection_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_env_injection_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(workflow_env_injection_gate, "POLICY", gov / "workflow_env_var_policy.json")
    monkeypatch.setattr(workflow_env_injection_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_env_injection_gate.main([]) == 0


def test_workflow_env_injection_gate_fails_on_unexpected_env_var(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(
        wf / "security.yml",
        "jobs:\n  a:\n    env:\n      GLYPHSER_ENV: ci\n      BAD_INJECTED_VAR: nope\n",
    )
    _write(
        gov / "workflow_env_var_policy.json",
        json.dumps(
            {
                "workflow_file_globs": ["*.yml"],
                "allowed_env_var_patterns": ["^GLYPHSER_[A-Z0-9_]+$"],
            }
        )
        + "\n",
    )
    monkeypatch.setattr(workflow_env_injection_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_env_injection_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(workflow_env_injection_gate, "POLICY", gov / "workflow_env_var_policy.json")
    monkeypatch.setattr(workflow_env_injection_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_env_injection_gate.main([]) == 1
    report = json.loads((sec / "workflow_env_injection_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("unexpected_env_var:.github/workflows/security.yml:BAD_INJECTED_VAR") for item in report["findings"])
