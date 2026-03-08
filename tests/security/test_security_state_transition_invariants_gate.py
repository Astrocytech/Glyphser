from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_state_transition_invariants_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def test_security_state_transition_invariants_gate_passes_for_consistent_states(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "temporary_waiver_gate.json", {"status": "PASS", "findings": [], "summary": {"active_waivers": 0}})
    _write(
        sec / "exception_waiver_reconciliation_gate.json",
        {"status": "PASS", "findings": [], "summary": {"missing_closures": 0}},
    )
    _write(
        sec / "promotion_policy_gate.json",
        {
            "status": "PASS",
            "findings": [],
            "summary": {"override_applied": False, "override_reason": "override_not_present", "soft_failures": []},
        },
    )

    monkeypatch.setattr(security_state_transition_invariants_gate, "ROOT", repo)
    monkeypatch.setattr(security_state_transition_invariants_gate, "evidence_root", lambda: repo / "evidence")
    assert security_state_transition_invariants_gate.main([]) == 0

    report = json.loads((sec / "security_state_transition_invariants_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["invariants_evaluated"] == ["ST-001", "ST-002", "ST-003", "ST-004"]


def test_security_state_transition_invariants_gate_fails_when_expired_waiver_allows_promotion(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "temporary_waiver_gate.json",
        {"status": "FAIL", "findings": ["expired_waiver:evidence/repro/waivers.json"], "summary": {"active_waivers": 0}},
    )
    _write(
        sec / "exception_waiver_reconciliation_gate.json",
        {"status": "PASS", "findings": [], "summary": {"missing_closures": 0}},
    )
    _write(
        sec / "promotion_policy_gate.json",
        {"status": "PASS", "findings": [], "summary": {"override_applied": False, "soft_failures": []}},
    )

    monkeypatch.setattr(security_state_transition_invariants_gate, "ROOT", repo)
    monkeypatch.setattr(security_state_transition_invariants_gate, "evidence_root", lambda: repo / "evidence")
    assert security_state_transition_invariants_gate.main([]) == 1

    report = json.loads((sec / "security_state_transition_invariants_gate.json").read_text(encoding="utf-8"))
    assert "invariant_violation:ST-001:expired_waiver_allows_promotion" in report["findings"]


def test_security_state_transition_invariants_gate_fails_invalid_override_transition(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "temporary_waiver_gate.json", {"status": "PASS", "findings": [], "summary": {"active_waivers": 0}})
    _write(
        sec / "exception_waiver_reconciliation_gate.json",
        {"status": "PASS", "findings": [], "summary": {"missing_closures": 0}},
    )
    _write(
        sec / "promotion_policy_gate.json",
        {
            "status": "PASS",
            "findings": [],
            "summary": {
                "override_applied": True,
                "override_reason": "override_not_present",
                "soft_failures": [],
            },
        },
    )

    monkeypatch.setattr(security_state_transition_invariants_gate, "ROOT", repo)
    monkeypatch.setattr(security_state_transition_invariants_gate, "evidence_root", lambda: repo / "evidence")
    assert security_state_transition_invariants_gate.main([]) == 1

    report = json.loads((sec / "security_state_transition_invariants_gate.json").read_text(encoding="utf-8"))
    assert "invariant_violation:ST-004:invalid_override_transition" in report["findings"]
