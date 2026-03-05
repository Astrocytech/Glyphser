from __future__ import annotations

import json
from pathlib import Path

from tooling.security import adversarial_campaign_plan_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_adversarial_campaign_plan_gate_passes_with_recent_campaign(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    plan = repo / "governance" / "security" / "adversarial_campaign_plan.json"
    sec.mkdir(parents=True)
    _write(
        plan,
        {
            "campaigns": [
                {
                    "campaign_id": "ADV-2026-Q1",
                    "planned_at_utc": "2026-02-10T00:00:00+00:00",
                    "scenario_coverage_matrix": [
                        {"scenario_id": "scenario-a", "coverage_status": "covered"},
                    ],
                    "signed_outcomes": [
                        {
                            "outcome_id": "ADV-1",
                            "executed_at_utc": "2026-02-20T00:00:00+00:00",
                            "outcome_signature": "ed25519:test",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(adversarial_campaign_plan_gate, "ROOT", repo)
    monkeypatch.setattr(adversarial_campaign_plan_gate, "PLAN_PATH", plan)
    monkeypatch.setattr(adversarial_campaign_plan_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")

    assert adversarial_campaign_plan_gate.main([]) == 0
    report = json.loads((sec / "adversarial_campaign_plan_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_adversarial_campaign_plan_gate_fails_for_stale_or_unsigned(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    plan = repo / "governance" / "security" / "adversarial_campaign_plan.json"
    sec.mkdir(parents=True)
    _write(
        plan,
        {
            "campaigns": [
                {
                    "campaign_id": "ADV-2025-Q1",
                    "planned_at_utc": "2025-01-10T00:00:00+00:00",
                    "scenario_coverage_matrix": [],
                    "signed_outcomes": [
                        {
                            "outcome_id": "ADV-OLD-1",
                            "executed_at_utc": "2025-01-20T00:00:00+00:00",
                            "outcome_signature": "",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(adversarial_campaign_plan_gate, "ROOT", repo)
    monkeypatch.setattr(adversarial_campaign_plan_gate, "PLAN_PATH", plan)
    monkeypatch.setattr(adversarial_campaign_plan_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")

    assert adversarial_campaign_plan_gate.main([]) == 1
    report = json.loads((sec / "adversarial_campaign_plan_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("adversarial_campaign_plan_stale:") for item in report["findings"])
    assert "missing_outcome_signature:ADV-2025-Q1" in report["findings"]
