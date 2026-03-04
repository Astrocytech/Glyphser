from __future__ import annotations

import json
from pathlib import Path

from tooling.security import incident_response_gate


def _policy(root: Path, *, stale: bool) -> dict[str, object]:
    ts = "2025-01-01T00:00:00Z" if stale else "2026-03-04T00:00:00Z"
    return {
        "max_runbook_age_days": 180,
        "max_alert_routing_age_days": 30,
        "max_key_rotation_drill_age_days": 90,
        "alert_routing_test": {
            "last_tested_utc": ts,
            "primary_contact": "oncall@glyphser.local",
            "secondary_contact": "security@glyphser.local",
            "escalation_contact": "sre-lead@glyphser.local",
        },
        "key_rotation_drill": {
            "last_drill_utc": ts,
            "evidence": "evidence/security/key_rotation_drill.json",
        },
        "runbooks": [
            {"path": "governance/security/OPERATIONS.md", "last_reviewed_utc": ts},
            {"path": "governance/security/THREAT_MODEL.md", "last_reviewed_utc": ts},
        ],
    }


def test_incident_response_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "OPERATIONS.md").write_text("ops\n", encoding="utf-8")
    (repo / "governance" / "security" / "THREAT_MODEL.md").write_text("threat\n", encoding="utf-8")
    (repo / "evidence" / "security" / "key_rotation_drill.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    (repo / "governance" / "security" / "incident_response_policy.json").write_text(
        json.dumps(_policy(repo, stale=False)) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(incident_response_gate, "ROOT", repo)
    monkeypatch.setattr(incident_response_gate, "evidence_root", lambda: repo / "evidence")
    assert incident_response_gate.main() == 0


def test_incident_response_gate_fails_on_stale_data(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "OPERATIONS.md").write_text("ops\n", encoding="utf-8")
    (repo / "governance" / "security" / "THREAT_MODEL.md").write_text("threat\n", encoding="utf-8")
    (repo / "governance" / "security" / "incident_response_policy.json").write_text(
        json.dumps(_policy(repo, stale=True)) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(incident_response_gate, "ROOT", repo)
    monkeypatch.setattr(incident_response_gate, "evidence_root", lambda: repo / "evidence")
    assert incident_response_gate.main() == 1
