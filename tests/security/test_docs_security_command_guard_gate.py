from __future__ import annotations

import json
from pathlib import Path

from tooling.security import docs_security_command_guard_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_docs_security_command_guard_gate_passes_when_docs_are_clean(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "docs_security_command_policy.json"
    _write_json(
        policy,
        {
            "scan_globs": ["docs/**/*.md"],
            "forbidden_patterns": [{"id": "disable_failfast", "pattern": "set\\s+\\+e\\b"}],
            "deprecated_guidance": [{"id": "old_semgrep", "contains": "python -m semgrep"}],
        },
    )
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "guide.md").write_text("Run `semgrep --config rules.yml`.\n", encoding="utf-8")

    monkeypatch.setattr(docs_security_command_guard_gate, "ROOT", repo)
    monkeypatch.setattr(docs_security_command_guard_gate, "POLICY", policy)
    monkeypatch.setattr(docs_security_command_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_security_command_guard_gate.main([]) == 0


def test_docs_security_command_guard_gate_fails_on_forbidden_or_outdated_commands(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "docs_security_command_policy.json"
    _write_json(
        policy,
        {
            "scan_globs": ["docs/**/*.md"],
            "forbidden_patterns": [{"id": "disable_failfast", "pattern": "set\\s+\\+e\\b"}],
            "deprecated_guidance": [{"id": "old_semgrep", "contains": "python -m semgrep"}],
        },
    )
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "unsafe.md").write_text(
        "```bash\nset +e\npython -m semgrep --config rules.yml\n```\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(docs_security_command_guard_gate, "ROOT", repo)
    monkeypatch.setattr(docs_security_command_guard_gate, "POLICY", policy)
    monkeypatch.setattr(docs_security_command_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_security_command_guard_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "docs_security_command_guard_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("forbidden_security_command_pattern:") for item in report["findings"])
    assert any(str(item).startswith("outdated_security_guidance:") for item in report["findings"])
