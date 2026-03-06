from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_runtime_budget_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_gate_runtime_budget_gate_passes_within_budget(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
        {
            "default_max_runtime_sec": 120,
            "per_gate_max_runtime_sec": {"tooling/security/foo.py": 5},
            "required_budget_gates": ["tooling/security/foo.py"],
            "trend_spike_multiplier": 3,
            "min_spike_seconds": 1,
        },
    )
    _write_json(
        ev / "security" / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/foo.py"], "runtime_seconds": 2.0},
            ]
        },
    )

    monkeypatch.setattr(security_gate_runtime_budget_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "POLICY",
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
    )
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "HISTORY",
        repo / "evidence" / "security" / "security_gate_runtime_history.json",
    )
    monkeypatch.setattr(security_gate_runtime_budget_gate, "evidence_root", lambda: ev)

    assert security_gate_runtime_budget_gate.main([]) == 0


def test_security_gate_runtime_budget_gate_fails_on_spike(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
        {
            "default_max_runtime_sec": 120,
            "required_budget_gates": ["tooling/security/foo.py"],
            "trend_spike_multiplier": 2,
            "min_spike_seconds": 1,
        },
    )
    _write_json(
        ev / "security" / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/foo.py"], "runtime_seconds": 10.0},
            ]
        },
    )
    _write_json(
        repo / "evidence" / "security" / "security_gate_runtime_history.json",
        {"schema_version": 1, "gate_runtimes": {"tooling/security/foo.py": [2.0, 2.5]}},
    )

    monkeypatch.setattr(security_gate_runtime_budget_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "POLICY",
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
    )
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "HISTORY",
        repo / "evidence" / "security" / "security_gate_runtime_history.json",
    )
    monkeypatch.setattr(security_gate_runtime_budget_gate, "evidence_root", lambda: ev)

    assert security_gate_runtime_budget_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_gate_runtime_budget_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("runtime_spike_detected:tooling/security/foo.py") for item in report["findings"])
    assert any(item.get("alarm") == "runtime_spike_detected" for item in report.get("regression_alarms", []))


def test_security_gate_runtime_budget_gate_fails_when_required_per_gate_budget_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
        {
            "default_max_runtime_sec": 120,
            "per_gate_max_runtime_sec": {},
            "required_budget_gates": ["tooling/security/foo.py"],
        },
    )
    _write_json(ev / "security" / "security_super_gate.json", {"results": []})

    monkeypatch.setattr(security_gate_runtime_budget_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "POLICY",
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
    )
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "HISTORY",
        repo / "evidence" / "security" / "security_gate_runtime_history.json",
    )
    monkeypatch.setattr(security_gate_runtime_budget_gate, "evidence_root", lambda: ev)

    assert security_gate_runtime_budget_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_gate_runtime_budget_gate.json").read_text(encoding="utf-8"))
    assert "missing_per_gate_budget:tooling/security/foo.py" in report["findings"]


def test_security_gate_runtime_budget_gate_fails_when_required_gate_runtime_not_observed(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
        {
            "default_max_runtime_sec": 120,
            "per_gate_max_runtime_sec": {"tooling/security/foo.py": 10},
            "required_budget_gates": ["tooling/security/foo.py"],
        },
    )
    _write_json(ev / "security" / "security_super_gate.json", {"results": []})

    monkeypatch.setattr(security_gate_runtime_budget_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "POLICY",
        repo / "governance" / "security" / "security_gate_runtime_budget_policy.json",
    )
    monkeypatch.setattr(
        security_gate_runtime_budget_gate,
        "HISTORY",
        repo / "evidence" / "security" / "security_gate_runtime_history.json",
    )
    monkeypatch.setattr(security_gate_runtime_budget_gate, "evidence_root", lambda: ev)

    assert security_gate_runtime_budget_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_gate_runtime_budget_gate.json").read_text(encoding="utf-8"))
    assert "missing_runtime_observation:tooling/security/foo.py" in report["findings"]
