from __future__ import annotations

import json
from pathlib import Path

from tooling.security import third_party_action_sha_mapping_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_third_party_action_sha_mapping_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "ci.yml", "steps:\n  - uses: actions/checkout@" + "a" * 40 + "\n")
    _write_json(
        repo / "governance" / "security" / "third_party_action_commit_map.json",
        {
            "expected_action_refs": {"actions/checkout": "a" * 40},
            "expected_action_provenance_urls": {"actions/checkout": "https://github.com/actions/checkout"},
        },
    )

    monkeypatch.setattr(third_party_action_sha_mapping_gate, "ROOT", repo)
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "POLICY", repo / "governance" / "security" / "third_party_action_commit_map.json")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "evidence_root", lambda: repo / "evidence")

    assert third_party_action_sha_mapping_gate.main([]) == 0


def test_third_party_action_sha_mapping_gate_fails_on_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "ci.yml", "steps:\n  - uses: actions/checkout@" + "a" * 40 + "\n")
    _write_json(
        repo / "governance" / "security" / "third_party_action_commit_map.json",
        {
            "expected_action_refs": {"actions/checkout": "b" * 40},
            "expected_action_provenance_urls": {"actions/checkout": "https://github.com/actions/checkout"},
        },
    )

    monkeypatch.setattr(third_party_action_sha_mapping_gate, "ROOT", repo)
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "POLICY", repo / "governance" / "security" / "third_party_action_commit_map.json")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "evidence_root", lambda: repo / "evidence")

    assert third_party_action_sha_mapping_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "third_party_action_sha_mapping_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("action_sha_mapping_drift:actions/checkout") for item in report["findings"])


def test_third_party_action_sha_mapping_gate_fails_when_provenance_url_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "ci.yml", "steps:\n  - uses: actions/checkout@" + "a" * 40 + "\n")
    _write_json(
        repo / "governance" / "security" / "third_party_action_commit_map.json",
        {"expected_action_refs": {"actions/checkout": "a" * 40}},
    )

    monkeypatch.setattr(third_party_action_sha_mapping_gate, "ROOT", repo)
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "POLICY", repo / "governance" / "security" / "third_party_action_commit_map.json")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(third_party_action_sha_mapping_gate, "evidence_root", lambda: repo / "evidence")

    assert third_party_action_sha_mapping_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "third_party_action_sha_mapping_gate.json").read_text(encoding="utf-8"))
    assert "missing_action_provenance_url:actions/checkout" in report["findings"]
