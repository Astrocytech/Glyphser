from __future__ import annotations

import json
from pathlib import Path

from tooling.security import post_incident_closure_gate


def test_post_incident_closure_gate_passes_with_verified_action_items(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
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


def test_post_incident_closure_gate_skips_without_artifact(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(post_incident_closure_gate, "ROOT", repo)
    monkeypatch.setattr(post_incident_closure_gate, "evidence_root", lambda: repo / "evidence")
    assert post_incident_closure_gate.main([]) == 0
