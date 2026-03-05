from __future__ import annotations

import json
from pathlib import Path

from tooling.security import archival_encryption_verification_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_archival_encryption_verification_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "archival_encryption_policy.json"
    evidence = repo / "evidence" / "security" / "archival_encryption_verification.json"
    _write(
        policy,
        {
            "encryption_algorithm": "AES-256-GCM",
            "key_management_system": "kms://vault/archive",
            "custody_owner": "security-governance",
            "custody_backup_owner": "platform-security",
            "key_rotation_days": 90,
            "max_unencrypted_age_hours": 1,
            "verification_evidence_path": "evidence/security/archival_encryption_verification.json",
        },
    )
    _write(evidence, {"status": "PASS", "verified_at_utc": "2026-03-05T00:00:00Z"})

    monkeypatch.setattr(archival_encryption_verification_gate, "ROOT", repo)
    monkeypatch.setattr(archival_encryption_verification_gate, "POLICY", policy)
    monkeypatch.setattr(archival_encryption_verification_gate, "evidence_root", lambda: repo / "evidence")

    assert archival_encryption_verification_gate.main([]) == 0


def test_archival_encryption_verification_gate_fails_when_evidence_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "archival_encryption_policy.json"
    _write(
        policy,
        {
            "encryption_algorithm": "AES-256-GCM",
            "key_management_system": "kms://vault/archive",
            "custody_owner": "security-governance",
            "custody_backup_owner": "platform-security",
            "key_rotation_days": 90,
            "max_unencrypted_age_hours": 1,
            "verification_evidence_path": "evidence/security/archival_encryption_verification.json",
        },
    )

    monkeypatch.setattr(archival_encryption_verification_gate, "ROOT", repo)
    monkeypatch.setattr(archival_encryption_verification_gate, "POLICY", policy)
    monkeypatch.setattr(archival_encryption_verification_gate, "evidence_root", lambda: repo / "evidence")

    assert archival_encryption_verification_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "archival_encryption_verification_gate.json").read_text(encoding="utf-8"))
    assert "missing_archival_encryption_verification_evidence" in report["findings"]
