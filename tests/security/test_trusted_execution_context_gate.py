from __future__ import annotations

import json
from pathlib import Path

from tooling.security import trusted_execution_context_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_policy(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_trusted_execution_context_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    _write(
        wf / "release.yml",
        "jobs:\n  a:\n    runs-on: ubuntu-latest\n    env:\n      GLYPHSER_ENV: \"ci\"\n",
    )
    _write_policy(
        gov / "trusted_execution_context_policy.json",
        {
            "workflow_types": {
                "release": {
                    "workflows": ["release.yml"],
                    "allowed_runs_on": ["ubuntu-latest"],
                    "required_env": {"GLYPHSER_ENV": "ci"},
                }
            }
        },
    )
    monkeypatch.setattr(trusted_execution_context_gate, "ROOT", repo)
    monkeypatch.setattr(trusted_execution_context_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(trusted_execution_context_gate, "POLICY", gov / "trusted_execution_context_policy.json")
    monkeypatch.setattr(trusted_execution_context_gate, "evidence_root", lambda: repo / "evidence")
    assert trusted_execution_context_gate.main([]) == 0


def test_trusted_execution_context_gate_fails_on_disallowed_context(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(
        wf / "release.yml",
        "jobs:\n  a:\n    runs-on: windows-latest\n",
    )
    _write_policy(
        gov / "trusted_execution_context_policy.json",
        {
            "workflow_types": {
                "release": {
                    "workflows": ["release.yml"],
                    "allowed_runs_on": ["ubuntu-latest"],
                    "required_env": {"GLYPHSER_ENV": "ci"},
                }
            }
        },
    )
    monkeypatch.setattr(trusted_execution_context_gate, "ROOT", repo)
    monkeypatch.setattr(trusted_execution_context_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(trusted_execution_context_gate, "POLICY", gov / "trusted_execution_context_policy.json")
    monkeypatch.setattr(trusted_execution_context_gate, "evidence_root", lambda: repo / "evidence")
    assert trusted_execution_context_gate.main([]) == 1
    report = json.loads((sec / "trusted_execution_context_gate.json").read_text(encoding="utf-8"))
    assert "disallowed_runs_on:release:release.yml:windows-latest" in report["findings"]
    assert "missing_required_env:release:release.yml:GLYPHSER_ENV" in report["findings"]
