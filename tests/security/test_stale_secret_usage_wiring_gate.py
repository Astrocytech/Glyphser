from __future__ import annotations

import json
from pathlib import Path

from tooling.security import stale_secret_usage_wiring_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_stale_secret_usage_wiring_gate_passes_when_referenced_secrets_are_fresh(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "release.yml", "env:\n  KEY: ${{ secrets.FOO_TOKEN }}\n")
    _write_json(repo / "governance" / "security" / "secret_management_policy.json", {"max_secret_rotation_age_days": 3650})
    _write_json(
        repo / "evidence" / "security" / "secret_rotation_audit.json",
        {
            "secret_rotation_metadata": {
                "FOO_TOKEN": {
                    "last_rotated_utc": "2026-03-01T00:00:00Z",
                    "rotation_method": "vault",
                    "rotation_ticket": "SEC-1",
                }
            }
        },
    )

    monkeypatch.setattr(stale_secret_usage_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "SECRET_POLICY", repo / "governance/security/secret_management_policy.json")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "ROTATION_AUDIT", repo / "evidence/security/secret_rotation_audit.json")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "WORKFLOWS", repo / ".github/workflows")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert stale_secret_usage_wiring_gate.main([]) == 0


def test_stale_secret_usage_wiring_gate_fails_on_missing_metadata(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "release.yml", "env:\n  KEY: ${{ secrets.FOO_TOKEN }}\n")
    _write_json(repo / "governance" / "security" / "secret_management_policy.json", {"max_secret_rotation_age_days": 3650})
    _write_json(repo / "evidence" / "security" / "secret_rotation_audit.json", {"secret_rotation_metadata": {}})

    monkeypatch.setattr(stale_secret_usage_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "SECRET_POLICY", repo / "governance/security/secret_management_policy.json")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "ROTATION_AUDIT", repo / "evidence/security/secret_rotation_audit.json")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "WORKFLOWS", repo / ".github/workflows")
    monkeypatch.setattr(stale_secret_usage_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert stale_secret_usage_wiring_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "stale_secret_usage_wiring_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_rotation_metadata_for_referenced_secret:FOO_TOKEN" in report["findings"]
