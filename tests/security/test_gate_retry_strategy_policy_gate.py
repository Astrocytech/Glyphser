from __future__ import annotations

import json
from pathlib import Path

from tooling.security import gate_retry_strategy_policy_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_gate_retry_strategy_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "gate_retry_strategy_policy.json"
    _write(
        policy,
        {
            "max_attempts": 2,
            "allowed_retry_gates": ["security_toolchain_gate"],
            "require_deterministic_seed": True,
            "retry_events_path": "evidence/security/gate_retry_events.json",
        },
    )
    _write(
        repo / "evidence" / "security" / "gate_retry_events.json",
        {"events": [{"gate": "security_toolchain_gate", "attempt": 2, "deterministic_seeded": True}]},
    )

    monkeypatch.setattr(gate_retry_strategy_policy_gate, "ROOT", repo)
    monkeypatch.setattr(gate_retry_strategy_policy_gate, "POLICY", policy)
    monkeypatch.setattr(gate_retry_strategy_policy_gate, "evidence_root", lambda: repo / "evidence")

    assert gate_retry_strategy_policy_gate.main([]) == 0


def test_gate_retry_strategy_policy_gate_fails_on_policy_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "gate_retry_strategy_policy.json"
    _write(
        policy,
        {
            "max_attempts": 1,
            "allowed_retry_gates": ["security_toolchain_gate"],
            "require_deterministic_seed": True,
            "retry_events_path": "evidence/security/gate_retry_events.json",
        },
    )
    _write(
        repo / "evidence" / "security" / "gate_retry_events.json",
        {"events": [{"gate": "other_gate", "attempt": 2, "deterministic_seeded": False}]},
    )

    monkeypatch.setattr(gate_retry_strategy_policy_gate, "ROOT", repo)
    monkeypatch.setattr(gate_retry_strategy_policy_gate, "POLICY", policy)
    monkeypatch.setattr(gate_retry_strategy_policy_gate, "evidence_root", lambda: repo / "evidence")

    assert gate_retry_strategy_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "gate_retry_strategy_policy_gate.json").read_text(encoding="utf-8"))
    assert "retry_gate_not_allowed:other_gate" in report["findings"]
    assert "retry_attempt_exceeds_max:other_gate:2:1" in report["findings"]
    assert "retry_missing_deterministic_seed:other_gate" in report["findings"]
