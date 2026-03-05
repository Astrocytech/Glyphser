from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_completed_item_proof_audit


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_completed_item_proof_audit_reopens_done_item_without_proof(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "code_diff_ref": "",
                    "test_diff_ref": "",
                    "ci_run_ref": "",
                    "negative_test_evidence_ref": "",
                    "evidence_link": "",
                    "regression_green_runs": 0,
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_completed_item_proof_audit, "ROOT", repo)
    monkeypatch.setattr(hardening_completed_item_proof_audit, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completed_item_proof_audit, "evidence_root", lambda: repo / "evidence")
    assert hardening_completed_item_proof_audit.main([]) == 1
    updated = json.loads(registry.read_text(encoding="utf-8"))
    assert updated["entries"][0]["status"] == "in_progress"


def test_hardening_completed_item_proof_audit_passes_when_proof_complete(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "code_diff_ref": "commit:abc",
                    "test_diff_ref": "commit:def",
                    "ci_run_ref": "workflow:123",
                    "negative_test_evidence_ref": "artifact:neg",
                    "evidence_link": "evidence/security/hardening_completed_item_proof_audit.json",
                    "regression_green_runs": 3,
                }
            ]
        },
    )
    monkeypatch.setattr(hardening_completed_item_proof_audit, "ROOT", repo)
    monkeypatch.setattr(hardening_completed_item_proof_audit, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completed_item_proof_audit, "evidence_root", lambda: repo / "evidence")
    assert hardening_completed_item_proof_audit.main([]) == 0
