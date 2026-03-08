from __future__ import annotations

import json
from pathlib import Path

from tooling.security import org_secret_backend_gate


def test_org_secret_backend_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "org_secret_backend_policy.json").write_text(
        json.dumps(
            {
                "required_backend_type": "org_secret_manager",
                "required_credential_mode": "short_lived",
                "max_credential_ttl_hours": 24,
                "snapshot_path": "evidence/security/org_secret_backend_snapshot.json",
                "required_secrets": ["A", "B"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "org_secret_backend_snapshot.json").write_text(
        json.dumps(
            {
                "backend_type": "org_secret_manager",
                "credential_mode": "short_lived",
                "credential_ttl_hours": 1,
                "managed_secrets": ["A", "B"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(org_secret_backend_gate, "ROOT", repo)
    monkeypatch.setattr(org_secret_backend_gate, "evidence_root", lambda: repo / "evidence")
    assert org_secret_backend_gate.main() == 0


def test_org_secret_backend_gate_fails_on_ttl(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "org_secret_backend_policy.json").write_text(
        json.dumps(
            {
                "required_backend_type": "org_secret_manager",
                "required_credential_mode": "short_lived",
                "max_credential_ttl_hours": 24,
                "snapshot_path": "evidence/security/org_secret_backend_snapshot.json",
                "required_secrets": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "org_secret_backend_snapshot.json").write_text(
        json.dumps(
            {
                "backend_type": "org_secret_manager",
                "credential_mode": "short_lived",
                "credential_ttl_hours": 72,
                "managed_secrets": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(org_secret_backend_gate, "ROOT", repo)
    monkeypatch.setattr(org_secret_backend_gate, "evidence_root", lambda: repo / "evidence")
    assert org_secret_backend_gate.main() == 1
