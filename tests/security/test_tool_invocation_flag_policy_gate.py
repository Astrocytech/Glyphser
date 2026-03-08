from __future__ import annotations

import json
from pathlib import Path

from tooling.security import tool_invocation_flag_policy_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_tool_invocation_flag_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "governance" / "security" / "tool_invocation_flag_policy.json",
        json.dumps(
            {
                "tools": [
                    {
                        "id": "semgrep",
                        "match": "semgrep --config tooling/security/semgrep-rules.yml",
                        "required_flags": ["--error", "--output"],
                        "required_any_flags": [["--sarif", "--json"]],
                        "forbidden_flags": ["--quiet"],
                    }
                ]
            }
        )
        + "\n",
    )
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  scan:\n    steps:\n      - run: semgrep --config tooling/security/semgrep-rules.yml --error --json --output semgrep.json runtime\n",
    )
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "ROOT", repo)
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "POLICY", repo / "governance" / "security" / "tool_invocation_flag_policy.json")
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert tool_invocation_flag_policy_gate.main([]) == 0


def test_tool_invocation_flag_policy_gate_fails_on_missing_required_flag(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = {
        "tools": [
            {
                "id": "bandit",
                "match": "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling",
                "required_flags": ["-l", "-ii"],
            }
        ]
    }
    _write(repo / "governance" / "security" / "tool_invocation_flag_policy.json", json.dumps(policy) + "\n")
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  scan:\n    steps:\n      - run: bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -l\n",
    )
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "ROOT", repo)
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "POLICY", repo / "governance" / "security" / "tool_invocation_flag_policy.json")
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(tool_invocation_flag_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert tool_invocation_flag_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "tool_invocation_flag_policy_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_required_flag:bandit:") for item in report["findings"])
