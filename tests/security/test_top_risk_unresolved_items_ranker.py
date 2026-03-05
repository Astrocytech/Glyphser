from __future__ import annotations

import json
from pathlib import Path

from tooling.security import top_risk_unresolved_items_ranker


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_top_risk_unresolved_items_ranker_orders_by_weighted_score(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    policy = repo / "governance" / "security" / "hardening_ticket_risk_scoring_policy.json"
    ev.mkdir(parents=True)
    _write(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-1",
                    "state": "OPEN",
                    "severity": 5,
                    "exploitability": 5,
                    "blast_radius": 4,
                    "created_at_utc": "2026-02-15T00:00:00+00:00",
                    "due_at_utc": "2026-03-01T00:00:00+00:00",
                },
                {
                    "ticket_id": "SEC-2",
                    "state": "OPEN",
                    "severity": 3,
                    "exploitability": 2,
                    "blast_radius": 2,
                    "created_at_utc": "2026-03-02T00:00:00+00:00",
                    "due_at_utc": "2026-03-10T00:00:00+00:00",
                },
                {
                    "ticket_id": "SEC-3",
                    "state": "CLOSED",
                    "severity": 5,
                    "exploitability": 5,
                    "blast_radius": 5,
                    "due_at_utc": "2026-02-10T00:00:00+00:00",
                },
            ]
        },
    )
    _write(
        policy,
        {
            "top_n": 5,
            "weights": {
                "severity": 3.0,
                "exploitability": 2.0,
                "blast_radius": 2.0,
                "overdue_days": 1.5,
                "age_days": 0.5,
            },
        },
    )
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "ROOT", repo)
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "DEFAULT_REGISTRY", registry)
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "DEFAULT_POLICY", policy)
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")

    assert top_risk_unresolved_items_ranker.main([]) == 0
    report = json.loads((ev / "top_risk_unresolved_items_ranker.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["unresolved_tickets"] == 2
    assert report["top_risk_unresolved_items"][0]["ticket_id"] == "SEC-1"
    assert [item["ticket_id"] for item in report["top_risk_unresolved_items"]] == ["SEC-1", "SEC-2"]
    assert "owner" in report["top_risk_unresolved_items"][0]
    assert "eta_utc" in report["top_risk_unresolved_items"][0]
    assert "confidence" in report["top_risk_unresolved_items"][0]


def test_top_risk_unresolved_items_ranker_fails_when_registry_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    policy = repo / "governance" / "security" / "hardening_ticket_risk_scoring_policy.json"
    _write(policy, {"top_n": 10, "weights": {"severity": 3}})
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "ROOT", repo)
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "DEFAULT_POLICY", policy)
    monkeypatch.setattr(top_risk_unresolved_items_ranker, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TICKET_STATE_PATH", str(repo / "governance" / "security" / "missing.json"))

    assert top_risk_unresolved_items_ranker.main([]) == 1
    report = json.loads((ev / "top_risk_unresolved_items_ranker.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_ticket_registry" in report["findings"]
