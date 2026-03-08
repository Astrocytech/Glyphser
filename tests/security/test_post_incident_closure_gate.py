from __future__ import annotations

import json
from pathlib import Path

from tooling.security import post_incident_closure_gate


def test_post_incident_closure_gate_passes_with_verified_action_items(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    test_file = repo / "tests" / "security" / "test_x.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_y():\n    assert True\n", encoding="utf-8")
    (sec / "post_incident_closure.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "incident_id": "INC-123",
                "action_items": [
                    {"id": "A1", "verification_test": "tests/security/test_x.py::test_y", "verified": True}
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(post_incident_closure_gate, "ROOT", repo)
    monkeypatch.setattr(post_incident_closure_gate, "evidence_root", lambda: repo / "evidence")
    assert post_incident_closure_gate.main([]) == 0


def test_post_incident_closure_gate_fails_when_test_reference_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "post_incident_closure.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "incident_id": "INC-456",
                "action_items": [
                    {"id": "A1", "verification_test": "tests/security/test_missing.py::test_case", "verified": True}
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(post_incident_closure_gate, "ROOT", repo)
    monkeypatch.setattr(post_incident_closure_gate, "evidence_root", lambda: repo / "evidence")
    assert post_incident_closure_gate.main([]) == 1
    report = json.loads((sec / "post_incident_closure_gate.json").read_text(encoding="utf-8"))
    assert "action_item_test_not_found:0" in report["findings"]


def test_post_incident_closure_gate_skips_without_artifact(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(post_incident_closure_gate, "ROOT", repo)
    monkeypatch.setattr(post_incident_closure_gate, "evidence_root", lambda: repo / "evidence")
    assert post_incident_closure_gate.main([]) == 0
