from __future__ import annotations

import json
from pathlib import Path

from tooling.security import secret_rotation_metadata_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_secret_rotation_metadata_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec_policy = repo / "governance" / "security" / "secret_management_policy.json"
    org_policy = repo / "governance" / "security" / "org_secret_backend_policy.json"
    audit = repo / "evidence" / "security" / "secret_rotation_audit.json"

    _write(sec_policy, {"max_secret_rotation_age_days": 3650, "rotation_audit_log": "evidence/security/secret_rotation_audit.json", "required_secrets": ["A"]})
    _write(org_policy, {"required_secrets": ["B"]})
    _write(
        audit,
        {
            "secrets_rotated": ["A", "B"],
            "secret_rotation_metadata": {
                "A": {
                    "last_rotated_utc": "2026-03-01T00:00:00Z",
                    "rotation_method": "vault",
                    "rotation_ticket": "SEC-1",
                },
                "B": {
                    "last_rotated_utc": "2026-03-01T00:00:00Z",
                    "rotation_method": "vault",
                    "rotation_ticket": "SEC-2",
                },
            },
        },
    )

    monkeypatch.setattr(secret_rotation_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(secret_rotation_metadata_gate, "SECRET_POLICY", sec_policy)
    monkeypatch.setattr(secret_rotation_metadata_gate, "ORG_POLICY", org_policy)
    monkeypatch.setattr(secret_rotation_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_rotation_metadata_gate.main([]) == 0


def test_secret_rotation_metadata_gate_fails_missing_metadata(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec_policy = repo / "governance" / "security" / "secret_management_policy.json"
    org_policy = repo / "governance" / "security" / "org_secret_backend_policy.json"
    audit = repo / "evidence" / "security" / "secret_rotation_audit.json"

    _write(sec_policy, {"max_secret_rotation_age_days": 3650, "rotation_audit_log": "evidence/security/secret_rotation_audit.json", "required_secrets": ["A"]})
    _write(org_policy, {"required_secrets": []})
    _write(audit, {"secrets_rotated": ["A"], "secret_rotation_metadata": {}})

    monkeypatch.setattr(secret_rotation_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(secret_rotation_metadata_gate, "SECRET_POLICY", sec_policy)
    monkeypatch.setattr(secret_rotation_metadata_gate, "ORG_POLICY", org_policy)
    monkeypatch.setattr(secret_rotation_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_rotation_metadata_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "secret_rotation_metadata_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_rotation_metadata:A" in report["findings"]
