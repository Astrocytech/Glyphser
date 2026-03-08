from __future__ import annotations

import json
from pathlib import Path

from tooling.security import external_action_owner_allowlist_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_external_action_owner_allowlist_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "ci.yml", "steps:\n  - uses: actions/checkout@sha\n")
    _write_json(repo / "governance" / "security" / "external_action_owner_allowlist.json", {"allowed_action_owners": ["actions"]})
    _write(repo / "governance" / "security" / "external_action_owner_allowlist.json.sig", "sig\n")

    class _Sign:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "key"

        @staticmethod
        def verify_file(path: Path, sig: str, *, key: str) -> bool:
            _ = path, sig, key
            return True

    monkeypatch.setattr(external_action_owner_allowlist_gate, "ROOT", repo)
    monkeypatch.setattr(external_action_owner_allowlist_gate, "POLICY", repo / "governance" / "security" / "external_action_owner_allowlist.json")
    monkeypatch.setattr(external_action_owner_allowlist_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(external_action_owner_allowlist_gate, "artifact_signing", _Sign)
    monkeypatch.setattr(external_action_owner_allowlist_gate, "evidence_root", lambda: repo / "evidence")

    assert external_action_owner_allowlist_gate.main([]) == 0


def test_external_action_owner_allowlist_gate_fails_on_disallowed_owner(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "ci.yml", "steps:\n  - uses: evilcorp/runner@sha\n")
    _write_json(repo / "governance" / "security" / "external_action_owner_allowlist.json", {"allowed_action_owners": ["actions"]})
    _write(repo / "governance" / "security" / "external_action_owner_allowlist.json.sig", "sig\n")

    class _Sign:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "key"

        @staticmethod
        def verify_file(path: Path, sig: str, *, key: str) -> bool:
            _ = path, sig, key
            return True

    monkeypatch.setattr(external_action_owner_allowlist_gate, "ROOT", repo)
    monkeypatch.setattr(external_action_owner_allowlist_gate, "POLICY", repo / "governance" / "security" / "external_action_owner_allowlist.json")
    monkeypatch.setattr(external_action_owner_allowlist_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(external_action_owner_allowlist_gate, "artifact_signing", _Sign)
    monkeypatch.setattr(external_action_owner_allowlist_gate, "evidence_root", lambda: repo / "evidence")

    assert external_action_owner_allowlist_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "external_action_owner_allowlist_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("disallowed_action_owner:evilcorp") for item in report["findings"])
