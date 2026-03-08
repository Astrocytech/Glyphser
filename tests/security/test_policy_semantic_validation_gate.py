from __future__ import annotations

import json
from pathlib import Path

from tooling.security import policy_semantic_validation_gate


def _write(repo: Path, rel: str, payload: dict[str, object]) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_policy_semantic_validation_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo,
        "governance/security/advanced_hardening_policy.json",
        {"max_attestation_age_hours": 168, "schema_strict_min_migration_pct": 95.0},
    )
    _write(
        repo,
        "governance/security/key_management_policy.json",
        {"minimum_key_length": 32, "minimum_entropy_bits": 96, "maximum_rotation_age_days": 90},
    )
    _write(
        repo,
        "governance/security/container_provenance_policy.json",
        {"cosign_required_lanes": ["release"], "cosign_skippable_lanes": ["ci"]},
    )
    monkeypatch.setattr(policy_semantic_validation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_semantic_validation_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_semantic_validation_gate.main([]) == 0


def test_policy_semantic_validation_gate_fails_on_invalid_ranges(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo,
        "governance/security/advanced_hardening_policy.json",
        {"max_attestation_age_hours": 0, "schema_strict_min_migration_pct": 120.0},
    )
    _write(
        repo,
        "governance/security/key_management_policy.json",
        {"minimum_key_length": 4, "minimum_entropy_bits": 1, "maximum_rotation_age_days": 0},
    )
    _write(
        repo,
        "governance/security/container_provenance_policy.json",
        {"cosign_required_lanes": ["release"], "cosign_skippable_lanes": ["release"]},
    )
    monkeypatch.setattr(policy_semantic_validation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_semantic_validation_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_semantic_validation_gate.main([]) == 1
