from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_unrelated_artifact_mutation_gate


class _Proc:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode
        self.stdout = ""
        self.stderr = ""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_security_unrelated_artifact_mutation_gate_passes_when_only_security_evidence_changes(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    policy = repo / "governance" / "security" / "security_unrelated_artifact_mutation_policy.json"
    _write_json(
        policy,
        {
            "probe_commands": [["python", "tooling/security/sample_gate.py"]],
            "allowed_mutation_prefixes": ["evidence/security/"],
        },
    )
    tracked = ["docs/guide.md", "evidence/security/sample_gate.json"]
    _write(repo / "docs" / "guide.md", "stable\n")
    _write(ev / "security" / "sample_gate.json", "v1\n")

    def _run_checked(*args, **kwargs):
        _ = args, kwargs
        _write(ev / "security" / "sample_gate.json", "v2\n")
        return _Proc(0)

    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "ROOT", repo)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "POLICY", policy)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "_tracked_paths", lambda _root: tracked)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "run_checked", _run_checked)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "evidence_root", lambda: ev)

    assert security_unrelated_artifact_mutation_gate.main([]) == 0


def test_security_unrelated_artifact_mutation_gate_fails_on_unexpected_source_mutation(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    policy = repo / "governance" / "security" / "security_unrelated_artifact_mutation_policy.json"
    _write_json(
        policy,
        {
            "probe_commands": [["python", "tooling/security/sample_gate.py"]],
            "allowed_mutation_prefixes": ["evidence/security/"],
        },
    )
    tracked = ["docs/guide.md"]
    guide = repo / "docs" / "guide.md"
    _write(guide, "stable\n")
    called = {"n": 0}

    def _run_checked(*args, **kwargs):
        _ = args, kwargs
        called["n"] += 1
        if called["n"] == 1:
            _write(guide, "mutated\n")
        return _Proc(0)

    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "ROOT", repo)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "POLICY", policy)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "_tracked_paths", lambda _root: tracked)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "run_checked", _run_checked)
    monkeypatch.setattr(security_unrelated_artifact_mutation_gate, "evidence_root", lambda: ev)

    assert security_unrelated_artifact_mutation_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_unrelated_artifact_mutation_gate.json").read_text(encoding="utf-8"))
    assert "unexpected_artifact_mutation:docs/guide.md" in report["findings"]
