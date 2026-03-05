from __future__ import annotations

import json
from pathlib import Path

from tooling.security import developer_mode_profile_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_developer_mode_profile_gate_passes_with_strict_flags_and_allowed_mocks(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "developer_mode_profile.json"
    _write(
        policy,
        {
            "required_strict_env_vars": ["GLYPHSER_STRICT_PREREQS", "GLYPHSER_STRICT_KEY"],
            "allowed_mock_attestations": ["mock_policy_signature"],
            "mock_attestations_env": "GLYPHSER_MOCK_ATTESTATIONS",
        },
    )

    monkeypatch.setattr(developer_mode_profile_gate, "ROOT", repo)
    monkeypatch.setattr(developer_mode_profile_gate, "POLICY", policy)
    monkeypatch.setattr(developer_mode_profile_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_PROFILE", "developer")
    monkeypatch.setenv("GLYPHSER_STRICT_PREREQS", "1")
    monkeypatch.setenv("GLYPHSER_STRICT_KEY", "true")
    monkeypatch.setenv("GLYPHSER_MOCK_ATTESTATIONS", '["mock_policy_signature"]')

    assert developer_mode_profile_gate.main([]) == 0


def test_developer_mode_profile_gate_fails_without_explicit_mock_attestations(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "developer_mode_profile.json"
    _write(
        policy,
        {
            "required_strict_env_vars": ["GLYPHSER_STRICT_PREREQS", "GLYPHSER_STRICT_KEY"],
            "allowed_mock_attestations": ["mock_policy_signature"],
            "mock_attestations_env": "GLYPHSER_MOCK_ATTESTATIONS",
        },
    )

    monkeypatch.setattr(developer_mode_profile_gate, "ROOT", repo)
    monkeypatch.setattr(developer_mode_profile_gate, "POLICY", policy)
    monkeypatch.setattr(developer_mode_profile_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_PROFILE", "developer")
    monkeypatch.setenv("GLYPHSER_STRICT_PREREQS", "1")
    monkeypatch.setenv("GLYPHSER_STRICT_KEY", "1")
    monkeypatch.setenv("GLYPHSER_MOCK_ATTESTATIONS", "")

    assert developer_mode_profile_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "developer_mode_profile_gate.json").read_text(encoding="utf-8"))
    assert "missing_explicit_mock_attestations" in report["findings"]
