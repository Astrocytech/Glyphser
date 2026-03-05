from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_freeze_criteria_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_freeze_criteria_gate_passes_for_trigger_backed_open_items(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    policy = repo / "governance" / "security" / "hardening_freeze_criteria_policy.json"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    _write_json(
        policy,
        {
            "allowed_trigger_types": ["incident", "audit"],
            "enforced_states": ["OPEN"],
            "enforced_ticket_registry_path": "governance/security/hardening_ticket_registry.json",
        },
    )
    _write_json(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-123",
                    "state": "OPEN",
                    "trigger_type": "incident",
                    "trigger_reference": "INC-2026-777",
                    "verification_plan": "pytest tests/security/test_hardening_freeze_criteria_gate.py",
                    "duplicate_check_reference": "todo-scan:A..AC",
                    "duplicate_check_result": "no_duplicate_category",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_freeze_criteria_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_freeze_criteria_gate.main([]) == 0


def test_hardening_freeze_criteria_gate_fails_without_trigger_reference(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    policy = repo / "governance" / "security" / "hardening_freeze_criteria_policy.json"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    _write_json(
        policy,
        {
            "allowed_trigger_types": ["incident", "audit"],
            "enforced_states": ["OPEN"],
            "enforced_ticket_registry_path": "governance/security/hardening_ticket_registry.json",
        },
    )
    _write_json(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-124",
                    "state": "OPEN",
                    "trigger_type": "incident",
                    "trigger_reference": "",
                    "verification_plan": "pytest tests/security/test_hardening_freeze_criteria_gate.py",
                    "duplicate_check_reference": "todo-scan:A..AC",
                    "duplicate_check_result": "no_duplicate_category",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_freeze_criteria_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_freeze_criteria_gate.main([]) == 1
    report = json.loads((ev / "hardening_freeze_criteria_gate.json").read_text(encoding="utf-8"))
    assert "missing_trigger_reference:SEC-124" in report["findings"]


def test_hardening_freeze_criteria_gate_fails_without_verification_plan(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    policy = repo / "governance" / "security" / "hardening_freeze_criteria_policy.json"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    _write_json(
        policy,
        {
            "allowed_trigger_types": ["incident", "audit"],
            "enforced_states": ["OPEN"],
            "enforced_ticket_registry_path": "governance/security/hardening_ticket_registry.json",
        },
    )
    _write_json(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-125",
                    "state": "OPEN",
                    "trigger_type": "incident",
                    "trigger_reference": "INC-2026-001",
                    "verification_plan": "",
                    "duplicate_check_reference": "todo-scan:A..AC",
                    "duplicate_check_result": "no_duplicate_category",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_freeze_criteria_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_freeze_criteria_gate.main([]) == 1
    report = json.loads((ev / "hardening_freeze_criteria_gate.json").read_text(encoding="utf-8"))
    assert "missing_verification_plan:SEC-125" in report["findings"]


def test_hardening_freeze_criteria_gate_fails_for_speculative_duplicate_category(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    policy = repo / "governance" / "security" / "hardening_freeze_criteria_policy.json"
    registry = repo / "governance" / "security" / "hardening_ticket_registry.json"
    _write_json(
        policy,
        {
            "allowed_trigger_types": ["incident", "audit"],
            "enforced_states": ["OPEN"],
            "enforced_ticket_registry_path": "governance/security/hardening_ticket_registry.json",
        },
    )
    _write_json(
        registry,
        {
            "tickets": [
                {
                    "ticket_id": "SEC-126",
                    "state": "OPEN",
                    "trigger_type": "incident",
                    "trigger_reference": "INC-2026-001",
                    "verification_plan": "pytest tests/security/test_hardening_freeze_criteria_gate.py",
                    "duplicate_check_reference": "todo-scan:A..AC",
                    "duplicate_check_result": "duplicate_category",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_freeze_criteria_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_freeze_criteria_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_freeze_criteria_gate.main([]) == 1
    report = json.loads((ev / "hardening_freeze_criteria_gate.json").read_text(encoding="utf-8"))
    assert "speculative_or_duplicate_category_not_allowed:SEC-126:duplicate_category" in report["findings"]
