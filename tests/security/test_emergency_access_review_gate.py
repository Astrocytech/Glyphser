from __future__ import annotations

import json
from pathlib import Path

from tooling.security import emergency_access_review_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_emergency_access_review_gate_passes_for_closed_attested_grant(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "emergency_access_policy.json"
    grants = repo / "governance" / "security" / "emergency_access_grants.json"

    _write(policy, {"grants_path": "governance/security/emergency_access_grants.json", "max_active_days": 7})
    _write(
        grants,
        {
            "grants": [
                {
                    "id": "EA-1",
                    "status": "closed",
                    "granted_at_utc": "2026-03-01T00:00:00Z",
                    "expires_at_utc": "2026-03-03T00:00:00Z",
                    "closure_attestation": {
                        "ticket": "SEC-9001",
                        "closed_at_utc": "2026-03-02T00:00:00Z",
                        "approved_by": "security-lead",
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(emergency_access_review_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_access_review_gate, "POLICY", policy)
    monkeypatch.setattr(emergency_access_review_gate, "evidence_root", lambda: repo / "evidence")

    assert emergency_access_review_gate.main([]) == 0


def test_emergency_access_review_gate_fails_on_expired_active_grant(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "emergency_access_policy.json"
    grants = repo / "governance" / "security" / "emergency_access_grants.json"

    _write(policy, {"grants_path": "governance/security/emergency_access_grants.json", "max_active_days": 7})
    _write(
        grants,
        {
            "grants": [
                {
                    "id": "EA-2",
                    "status": "active",
                    "granted_at_utc": "2020-03-01T00:00:00Z",
                    "expires_at_utc": "2020-03-02T00:00:00Z",
                }
            ]
        },
    )

    monkeypatch.setattr(emergency_access_review_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_access_review_gate, "POLICY", policy)
    monkeypatch.setattr(emergency_access_review_gate, "evidence_root", lambda: repo / "evidence")

    assert emergency_access_review_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "emergency_access_review_gate.json").read_text(encoding="utf-8"))
    assert "active_grant_expired:EA-2" in report["findings"]
