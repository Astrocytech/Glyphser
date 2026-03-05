from __future__ import annotations

import json
from pathlib import Path

from tooling.security import gate_decommissioning_policy_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_gate_decommissioning_policy_gate_passes_with_replacement_proof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "gate_decommissioning_policy.json",
        {
            "decommission_records": [
                {
                    "obsolete_gate": "a.py",
                    "replacement_gate": "b.py",
                    "replacement_proof_artifact": "evidence/security/b.json",
                }
            ]
        },
    )
    monkeypatch.setattr(gate_decommissioning_policy_gate, "ROOT", repo)
    monkeypatch.setattr(
        gate_decommissioning_policy_gate,
        "POLICY",
        repo / "governance" / "security" / "gate_decommissioning_policy.json",
    )
    monkeypatch.setattr(gate_decommissioning_policy_gate, "evidence_root", lambda: ev)
    assert gate_decommissioning_policy_gate.main([]) == 0


def test_gate_decommissioning_policy_gate_fails_when_proof_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "gate_decommissioning_policy.json",
        {"decommission_records": [{"obsolete_gate": "a.py", "replacement_gate": "b.py"}]},
    )
    monkeypatch.setattr(gate_decommissioning_policy_gate, "ROOT", repo)
    monkeypatch.setattr(
        gate_decommissioning_policy_gate,
        "POLICY",
        repo / "governance" / "security" / "gate_decommissioning_policy.json",
    )
    monkeypatch.setattr(gate_decommissioning_policy_gate, "evidence_root", lambda: ev)
    assert gate_decommissioning_policy_gate.main([]) == 1
    report = json.loads((ev / "security" / "gate_decommissioning_policy_gate.json").read_text(encoding="utf-8"))
    assert "missing_replacement_proof_artifact:0" in report["findings"]
