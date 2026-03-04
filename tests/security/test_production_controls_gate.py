from __future__ import annotations

import json
from pathlib import Path

from tooling.security import production_controls_gate


def test_production_controls_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "production_controls_policy.json").write_text(
        json.dumps(
            {
                "required_controls": ["waf_ingress", "siem_pipeline", "oncall_paging"],
                "max_snapshot_age_days": 30,
                "snapshot_path": "evidence/security/production_controls_snapshot.json",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "production_controls_snapshot.json").write_text(
        json.dumps(
            {
                "updated_utc": "2026-03-04T00:00:00Z",
                "controls": {
                    "waf_ingress": {"enabled": True},
                    "siem_pipeline": {"enabled": True},
                    "oncall_paging": {"enabled": True},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(production_controls_gate, "ROOT", repo)
    monkeypatch.setattr(production_controls_gate, "evidence_root", lambda: repo / "evidence")
    assert production_controls_gate.main() == 0


def test_production_controls_gate_fails_when_control_disabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "production_controls_policy.json").write_text(
        json.dumps(
            {
                "required_controls": ["waf_ingress"],
                "max_snapshot_age_days": 30,
                "snapshot_path": "evidence/security/production_controls_snapshot.json",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "production_controls_snapshot.json").write_text(
        json.dumps({"updated_utc": "2026-03-04T00:00:00Z", "controls": {"waf_ingress": {"enabled": False}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(production_controls_gate, "ROOT", repo)
    monkeypatch.setattr(production_controls_gate, "evidence_root", lambda: repo / "evidence")
    assert production_controls_gate.main() == 1
