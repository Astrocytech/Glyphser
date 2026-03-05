from __future__ import annotations

import json
from pathlib import Path

from tooling.security import expired_degraded_mode_allowance_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_expired_degraded_mode_allowance_gate_passes_when_expired_allowance_is_inactive(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "temporary_waiver_policy.json",
        {"waiver_file_glob": "evidence/repro/waivers.json"},
    )
    _write_json(
        repo / "evidence" / "repro" / "waivers.json",
        {
            "waivers": [
                {
                    "id": "W-1",
                    "expires_at_utc": "2000-01-01T00:00:00+00:00",
                    "active": False,
                }
            ]
        },
    )

    monkeypatch.setattr(expired_degraded_mode_allowance_gate, "ROOT", repo)
    monkeypatch.setattr(expired_degraded_mode_allowance_gate, "evidence_root", lambda: ev)
    assert expired_degraded_mode_allowance_gate.main([]) == 0


def test_expired_degraded_mode_allowance_gate_fails_when_expired_allowance_is_active(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "temporary_waiver_policy.json",
        {"waiver_file_glob": "evidence/repro/waivers.json"},
    )
    _write_json(
        repo / "evidence" / "repro" / "waivers.json",
        {
            "waivers": [
                {
                    "id": "W-1",
                    "expires_at_utc": "2000-01-01T00:00:00+00:00",
                    "active": True,
                }
            ]
        },
    )

    monkeypatch.setattr(expired_degraded_mode_allowance_gate, "ROOT", repo)
    monkeypatch.setattr(expired_degraded_mode_allowance_gate, "evidence_root", lambda: ev)
    assert expired_degraded_mode_allowance_gate.main([]) == 1
    report = json.loads((ev / "security" / "expired_degraded_mode_allowance_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("expired_active_degraded_allowance:W-1:") for item in report["findings"])
