from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_stale_ticket_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_hardening_stale_ticket_gate_fails_on_past_due_open_ticket(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    ev.mkdir(parents=True)
    _write(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-101",
                    "owner": "sec-team",
                    "state": "OPEN",
                    "due_at_utc": "2026-03-01T00:00:00+00:00",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_stale_ticket_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_stale_ticket_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TICKET_STATE_PATH", str(registry))
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert hardening_stale_ticket_gate.main([]) == 1
    report = json.loads((ev / "hardening_stale_ticket_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["summary"]["stale_tickets"] == 1
    assert any(str(item).startswith("stale_ticket:SEC-101:") for item in report["findings"])


def test_hardening_stale_ticket_gate_passes_when_only_closed_or_not_due(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    ev.mkdir(parents=True)
    _write(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-201",
                    "owner": "sec-team",
                    "state": "CLOSED",
                    "due_at_utc": "2026-03-01T00:00:00+00:00",
                },
                {
                    "ticket_id": "SEC-202",
                    "owner": "sec-team",
                    "state": "OPEN",
                    "due_at_utc": "2026-03-10T00:00:00+00:00",
                },
            ]
        },
    )
    monkeypatch.setattr(hardening_stale_ticket_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_stale_ticket_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TICKET_STATE_PATH", str(registry))
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert hardening_stale_ticket_gate.main([]) == 0
    report = json.loads((ev / "hardening_stale_ticket_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["stale_tickets"] == 0


def test_hardening_stale_ticket_gate_fails_when_registry_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    monkeypatch.setattr(hardening_stale_ticket_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_stale_ticket_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_HARDENING_TICKET_STATE_PATH", str(repo / "governance" / "security" / "missing.json"))

    assert hardening_stale_ticket_gate.main([]) == 1
    report = json.loads((ev / "hardening_stale_ticket_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_ticket_registry" in report["findings"]
