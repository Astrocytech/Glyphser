from __future__ import annotations

import json
from pathlib import Path

from tooling.security import secret_management_gate


def test_secret_management_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "secret_management_policy.json").write_text(
        json.dumps(
            {
                "required_backend": "external_manager",
                "max_secret_rotation_age_days": 90,
                "rotation_audit_log": "evidence/security/secret_rotation_audit.json",
                "required_secrets": ["A", "B"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "secret_rotation_audit.json").write_text(
        json.dumps(
            {
                "backend": "external_manager",
                "last_rotation_utc": "2026-03-04T00:00:00Z",
                "secrets_rotated": ["A", "B"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(secret_management_gate, "ROOT", repo)
    monkeypatch.setattr(secret_management_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_management_gate.main() == 0


def test_secret_management_gate_fails_on_backend_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "secret_management_policy.json").write_text(
        json.dumps(
            {
                "required_backend": "external_manager",
                "max_secret_rotation_age_days": 90,
                "rotation_audit_log": "evidence/security/secret_rotation_audit.json",
                "required_secrets": ["A"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "secret_rotation_audit.json").write_text(
        json.dumps(
            {
                "backend": "local_env",
                "last_rotation_utc": "2026-03-04T00:00:00Z",
                "secrets_rotated": ["A"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(secret_management_gate, "ROOT", repo)
    monkeypatch.setattr(secret_management_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_management_gate.main() == 1
