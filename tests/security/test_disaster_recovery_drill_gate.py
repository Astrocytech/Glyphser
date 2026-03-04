from __future__ import annotations

import json
from pathlib import Path

from tooling.security import disaster_recovery_drill_gate


def test_disaster_recovery_drill_gate_passes_with_rto_rpo(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "evidence" / "security" / "disaster_recovery_drill.json"
    drill.parent.mkdir(parents=True, exist_ok=True)
    drill.write_text(
        json.dumps(
            {
                "status": "PASS",
                "restored_from_cold_backup": True,
                "integrity_verified": True,
                "provenance_verified": True,
                "rto_minutes": 15,
                "rpo_minutes": 5,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(disaster_recovery_drill_gate, "ROOT", repo)
    monkeypatch.setattr(disaster_recovery_drill_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        disaster_recovery_drill_gate,
        "load_stage_s_policy",
        lambda: {"drills": {"disaster_recovery_path": "evidence/security/disaster_recovery_drill.json"}},
    )
    assert disaster_recovery_drill_gate.main([]) == 0


def test_disaster_recovery_drill_gate_fails_missing_rto_rpo(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "evidence" / "security" / "disaster_recovery_drill.json"
    drill.parent.mkdir(parents=True, exist_ok=True)
    drill.write_text(
        json.dumps(
            {
                "status": "PASS",
                "restored_from_cold_backup": True,
                "integrity_verified": True,
                "provenance_verified": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(disaster_recovery_drill_gate, "ROOT", repo)
    monkeypatch.setattr(disaster_recovery_drill_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        disaster_recovery_drill_gate,
        "load_stage_s_policy",
        lambda: {"drills": {"disaster_recovery_path": "evidence/security/disaster_recovery_drill.json"}},
    )
    assert disaster_recovery_drill_gate.main([]) == 1
