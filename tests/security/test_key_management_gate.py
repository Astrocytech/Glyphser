from __future__ import annotations

import json
from pathlib import Path

from tooling.security import key_management_gate


def _setup_repo(repo: Path) -> None:
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (gov / "key_management_policy.json").write_text(
        json.dumps(
            {
                "minimum_key_length": 8,
                "minimum_entropy_bits": 10,
                "maximum_rotation_age_days": 365,
                "rotation_timestamp_env": "ROT_TS",
                "signing_key_env": "ROT_KEY",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_key_management_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _setup_repo(repo)
    monkeypatch.setattr(key_management_gate, "ROOT", repo)
    monkeypatch.setattr(key_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("ROT_KEY", "ComplexKeyMaterial123!@#")
    monkeypatch.setenv("ROT_TS", "2026-03-01T00:00:00+00:00")
    assert key_management_gate.main([]) == 0


def test_key_management_gate_fails_on_weak_key(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _setup_repo(repo)
    monkeypatch.setattr(key_management_gate, "ROOT", repo)
    monkeypatch.setattr(key_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("ROT_KEY", "aaaa")
    monkeypatch.setenv("ROT_TS", "2026-03-01T00:00:00+00:00")
    assert key_management_gate.main([]) == 1
