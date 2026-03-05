from __future__ import annotations

import json
from pathlib import Path

from tooling.security import ownership_continuity_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_ownership_continuity_gate_passes_with_defaults(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "governance" / "security" / "p.json", {"a": 1})
    _write(repo / "tooling" / "security" / "x_gate.py", "print('x')\n")
    _write(repo / ".github" / "workflows" / "a.yml", "name: a\n")
    _write_json(
        repo / "governance" / "security" / "ownership_registry.json",
        {
            "default_policy_owner": "o1",
            "default_policy_fallback_owner": "o1b",
            "default_gate_owner": "o2",
            "default_gate_fallback_owner": "o2b",
            "default_workflow_owner": "o3",
            "default_workflow_fallback_owner": "o3b",
        },
    )

    monkeypatch.setattr(ownership_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(ownership_continuity_gate, "REGISTRY", repo / "governance" / "security" / "ownership_registry.json")
    monkeypatch.setattr(ownership_continuity_gate, "evidence_root", lambda: repo / "evidence")

    assert ownership_continuity_gate.main([]) == 0


def test_ownership_continuity_gate_fails_when_unowned(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "governance" / "security" / "p.json", {"a": 1})
    _write(repo / "tooling" / "security" / "x_gate.py", "print('x')\n")
    _write(repo / ".github" / "workflows" / "a.yml", "name: a\n")
    _write_json(repo / "governance" / "security" / "ownership_registry.json", {})

    monkeypatch.setattr(ownership_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(ownership_continuity_gate, "REGISTRY", repo / "governance" / "security" / "ownership_registry.json")
    monkeypatch.setattr(ownership_continuity_gate, "evidence_root", lambda: repo / "evidence")

    assert ownership_continuity_gate.main([]) == 1


def test_ownership_continuity_gate_fails_when_fallback_matches_primary(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "governance" / "security" / "p.json", {"a": 1})
    _write(repo / "tooling" / "security" / "x_gate.py", "print('x')\n")
    _write(repo / ".github" / "workflows" / "a.yml", "name: a\n")
    _write_json(
        repo / "governance" / "security" / "ownership_registry.json",
        {
            "default_policy_owner": "o1",
            "default_policy_fallback_owner": "o1",
            "default_gate_owner": "o2",
            "default_gate_fallback_owner": "o2b",
            "default_workflow_owner": "o3",
            "default_workflow_fallback_owner": "o3b",
        },
    )

    monkeypatch.setattr(ownership_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(ownership_continuity_gate, "REGISTRY", repo / "governance" / "security" / "ownership_registry.json")
    monkeypatch.setattr(ownership_continuity_gate, "evidence_root", lambda: repo / "evidence")
    assert ownership_continuity_gate.main([]) == 1
