from __future__ import annotations

import json
from pathlib import Path

from tooling.security import emergency_lockdown_gate


def test_emergency_lockdown_gate_passes_for_disabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "emergency_lockdown_policy.json"
    policy.write_text(
        json.dumps(
            {
                "lockdown_enabled": False,
                "disable_publish": False,
                "disable_replay": False,
                "reason": "",
                "approved_by": [],
                "expires_at_utc": "",
                "updated_at_utc": "2026-03-04T00:00:00+00:00",
                "override_policy": {"required_distinct_approvals": 2, "max_override_duration_hours": 24},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from runtime.glyphser.security.artifact_signing import current_key, sign_file

    policy.with_suffix(".json.sig").write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(emergency_lockdown_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_lockdown_gate, "evidence_root", lambda: repo / "evidence")
    assert emergency_lockdown_gate.main([]) == 0


def test_emergency_lockdown_gate_fails_without_distinct_dual_approvals(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "emergency_lockdown_policy.json"
    policy.write_text(
        json.dumps(
            {
                "lockdown_enabled": True,
                "disable_publish": True,
                "disable_replay": True,
                "reason": "incident",
                "approved_by": ["alice"],
                "expires_at_utc": "2099-01-01T01:00:00+00:00",
                "updated_at_utc": "2099-01-01T00:00:00+00:00",
                "override_policy": {"required_distinct_approvals": 2, "max_override_duration_hours": 24},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from runtime.glyphser.security.artifact_signing import current_key, sign_file

    policy.with_suffix(".json.sig").write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(emergency_lockdown_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_lockdown_gate, "evidence_root", lambda: repo / "evidence")
    assert emergency_lockdown_gate.main([]) == 1


def test_emergency_lockdown_gate_fails_when_expiry_exceeds_auto_expiration_window(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "emergency_lockdown_policy.json"
    policy.write_text(
        json.dumps(
            {
                "lockdown_enabled": True,
                "disable_publish": True,
                "disable_replay": True,
                "reason": "incident",
                "approved_by": ["alice", "bob"],
                "expires_at_utc": "2099-01-03T00:30:00+00:00",
                "updated_at_utc": "2099-01-01T00:00:00+00:00",
                "override_policy": {"required_distinct_approvals": 2, "max_override_duration_hours": 24},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from runtime.glyphser.security.artifact_signing import current_key, sign_file

    policy.with_suffix(".json.sig").write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(emergency_lockdown_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_lockdown_gate, "evidence_root", lambda: repo / "evidence")
    assert emergency_lockdown_gate.main([]) == 1
