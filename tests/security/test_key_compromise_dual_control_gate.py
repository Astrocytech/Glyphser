from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import key_compromise_dual_control_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_key_compromise_dual_control_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    drill = ev / "key_compromise_drill.json"
    now = datetime.now(UTC)
    payload = {
        "primary_approver": "alice",
        "secondary_approver": "bob",
        "rotation_completed": True,
        "revocation_list_updated": True,
        "toggle_approval": {
            "ticket_id": "SEC-1234",
            "approved_at_utc": (now - timedelta(minutes=10)).isoformat(),
        },
        "emergency_disable_exercised": True,
        "disable_executed_at_utc": (now - timedelta(minutes=9)).isoformat(),
        "restored_at_utc": (now - timedelta(minutes=1)).isoformat(),
        "restoration_verified": True,
    }
    _write(drill, payload)
    drill.with_suffix(".json.sig").write_text(sign_file(drill, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(key_compromise_dual_control_gate, "ROOT", repo)
    monkeypatch.setattr(key_compromise_dual_control_gate, "evidence_root", lambda: repo / "evidence")
    assert key_compromise_dual_control_gate.main([]) == 0


def test_key_compromise_dual_control_gate_fails_missing_emergency_restore_proof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    drill = ev / "key_compromise_drill.json"
    payload = {
        "primary_approver": "alice",
        "secondary_approver": "alice",
        "rotation_completed": False,
        "revocation_list_updated": False,
        "toggle_approval": {"ticket_id": "", "approved_at_utc": "not-a-date"},
        "emergency_disable_exercised": True,
        "disable_executed_at_utc": "2026-01-01T00:00:00+00:00",
        "restored_at_utc": "2025-12-31T00:00:00+00:00",
        "restoration_verified": False,
    }
    _write(drill, payload)
    drill.with_suffix(".json.sig").write_text(sign_file(drill, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(key_compromise_dual_control_gate, "ROOT", repo)
    monkeypatch.setattr(key_compromise_dual_control_gate, "evidence_root", lambda: repo / "evidence")
    assert key_compromise_dual_control_gate.main([]) == 1
