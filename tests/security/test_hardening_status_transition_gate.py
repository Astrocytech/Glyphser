from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_status_transition_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_status_transition_gate_passes_with_allowed_transition(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_status_transition_policy.json"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        policy,
        {
            "allowed_statuses": ["pending", "in_progress", "done"],
            "allowed_transitions": {"pending": ["pending", "in_progress"], "in_progress": ["in_progress", "done"], "done": ["done"]},
            "done_requires_verification_proof": True,
        },
    )
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "verification_proof": "workflow:123",
                    "negative_test_evidence_ref": "gate:hardening_status_transition_gate:fail-123",
                    "verification": {
                        "tests_passed_ref": "pytest:tests/security/test_hardening_status_transition_gate.py",
                        "gate_passed_ref": "gate:hardening_status_transition_gate",
                        "ci_lane_ref": "ci:security-maintenance",
                    },
                    "ci_run_ref": "github-actions://security-maintenance/123456",
                    "evidence_link": "evidence/security/hardening_status_transition_gate.json",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_status_transition_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_status_transition_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_status_transition_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_status_transition_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_status_transition_gate.main([]) == 0


def test_hardening_status_transition_gate_fails_without_done_proof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_status_transition_policy.json"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        policy,
        {
            "allowed_statuses": ["pending", "in_progress", "done"],
            "allowed_transitions": {"pending": ["pending", "in_progress"], "in_progress": ["in_progress", "done"], "done": ["done"]},
            "done_requires_verification_proof": True,
        },
    )
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "verification_proof": "",
                    "negative_test_evidence_ref": "gate:hardening_status_transition_gate:fail-123",
                    "verification": {},
                    "ci_run_ref": "",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_status_transition_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_status_transition_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_status_transition_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_status_transition_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_status_transition_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_status_transition_gate.json").read_text(encoding="utf-8"))
    assert "missing_verification_proof_for_done:SEC-HARD-0001" in report["findings"]


def test_hardening_status_transition_gate_fails_without_pre_failure_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_status_transition_policy.json"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        policy,
        {
            "allowed_statuses": ["pending", "in_progress", "done"],
            "allowed_transitions": {"pending": ["pending", "in_progress"], "in_progress": ["in_progress", "done"], "done": ["done"]},
            "done_requires_verification_proof": True,
            "implementation_requires_pre_failure_evidence": True,
        },
    )
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "in_progress",
                    "previous_status": "pending",
                    "verification_proof": "",
                    "negative_test_evidence_ref": "",
                    "verification": {},
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_status_transition_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_status_transition_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_status_transition_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_status_transition_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_status_transition_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_status_transition_gate.json").read_text(encoding="utf-8"))
    assert "missing_pre_failure_evidence_for_implementation:SEC-HARD-0001" in report["findings"]


def test_hardening_status_transition_gate_fails_without_post_implementation_proof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_status_transition_policy.json"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        policy,
        {
            "allowed_statuses": ["pending", "in_progress", "done"],
            "allowed_transitions": {"pending": ["pending", "in_progress"], "in_progress": ["in_progress", "done"], "done": ["done"]},
            "done_requires_verification_proof": True,
            "implementation_requires_pre_failure_evidence": True,
            "done_requires_post_implementation_proof": True,
            "done_required_post_implementation_fields": ["tests_passed_ref", "gate_passed_ref", "ci_lane_ref"],
        },
    )
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "verification_proof": "workflow:123",
                    "negative_test_evidence_ref": "gate:hardening_status_transition_gate:fail-123",
                    "verification": {"tests_passed_ref": "pytest:pass"},
                    "ci_run_ref": "",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_status_transition_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_status_transition_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_status_transition_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_status_transition_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_status_transition_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_status_transition_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_post_implementation_proof_for_done:SEC-HARD-0001:") for item in report["findings"])
    assert "missing_ci_run_ref_for_done:SEC-HARD-0001" in report["findings"]


def test_hardening_status_transition_gate_fails_without_evidence_link(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_status_transition_policy.json"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        policy,
        {
            "allowed_statuses": ["pending", "in_progress", "done"],
            "allowed_transitions": {"pending": ["pending", "in_progress"], "in_progress": ["in_progress", "done"], "done": ["done"]},
            "done_requires_verification_proof": True,
            "implementation_requires_pre_failure_evidence": True,
            "done_requires_post_implementation_proof": True,
            "done_required_post_implementation_fields": ["tests_passed_ref", "gate_passed_ref", "ci_lane_ref"],
            "done_requires_evidence_link": True,
        },
    )
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "verification_proof": "workflow:123",
                    "negative_test_evidence_ref": "gate:hardening_status_transition_gate:fail-123",
                    "verification": {
                        "tests_passed_ref": "pytest:pass",
                        "gate_passed_ref": "gate:pass",
                        "ci_lane_ref": "ci:security",
                    },
                    "ci_run_ref": "github-actions://security/123",
                    "evidence_link": "",
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_status_transition_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_status_transition_gate, "POLICY", policy)
    monkeypatch.setattr(hardening_status_transition_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_status_transition_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_status_transition_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_status_transition_gate.json").read_text(encoding="utf-8"))
    assert "missing_evidence_link_for_done:SEC-HARD-0001" in report["findings"]
