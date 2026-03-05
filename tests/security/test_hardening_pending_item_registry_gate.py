from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_pending_item_registry_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_pending_item_registry_gate_passes_when_counts_and_ids_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A. Alpha\n[ ] first\n", encoding="utf-8")
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "owner": "unassigned",
                    "priority": "P3 opportunistic",
                    "milestone": "TBD",
                    "target_date": "",
                    "dependencies": [],
                    "verification": {},
                    "evidence_link": "",
                    "status": "pending",
                    "previous_status": "pending",
                    "verification_proof": "",
                    "code_diff_ref": "",
                    "test_diff_ref": "",
                    "ci_run_ref": "",
                    "negative_test_evidence_ref": "",
                    "regression_green_runs": 0,
                }
            ]
        },
    )

    monkeypatch.setattr(hardening_pending_item_registry_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "TODO", todo)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_pending_item_registry_gate.main([]) == 0


def test_hardening_pending_item_registry_gate_fails_on_duplicate_id(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A. Alpha\n[ ] first\n[ ] second\n", encoding="utf-8")
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "owner": "unassigned",
                    "priority": "P3 opportunistic",
                    "milestone": "TBD",
                    "target_date": "",
                    "dependencies": [],
                    "verification": {},
                    "evidence_link": "",
                    "status": "pending",
                    "previous_status": "pending",
                    "verification_proof": "",
                    "code_diff_ref": "",
                    "test_diff_ref": "",
                    "ci_run_ref": "",
                    "negative_test_evidence_ref": "",
                    "regression_green_runs": 0,
                },
                {
                    "id": "SEC-HARD-0001",
                    "owner": "unassigned",
                    "priority": "P3 opportunistic",
                    "milestone": "TBD",
                    "target_date": "",
                    "dependencies": [],
                    "verification": {},
                    "evidence_link": "",
                    "status": "pending",
                    "previous_status": "pending",
                    "verification_proof": "",
                    "code_diff_ref": "",
                    "test_diff_ref": "",
                    "ci_run_ref": "",
                    "negative_test_evidence_ref": "",
                    "regression_green_runs": 0,
                },
            ]
        },
    )

    monkeypatch.setattr(hardening_pending_item_registry_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "TODO", todo)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "REGISTRY", registry)
    monkeypatch.setattr(hardening_pending_item_registry_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_pending_item_registry_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_pending_item_registry_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("duplicate_pending_item_id:") for item in report["findings"])
