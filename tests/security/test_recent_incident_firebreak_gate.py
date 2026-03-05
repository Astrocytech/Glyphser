from __future__ import annotations

import json
from pathlib import Path

from tooling.security import recent_incident_firebreak_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
        return
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_recent_incident_firebreak_gate_passes_when_required_reports_are_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "recent_incident_firebreak_policy.json"
    _write(
        policy,
        {
            "active_incidents": [
                {
                    "incident_id": "INC-1",
                    "affected_paths": ["tooling/security"],
                    "required_reports": ["incident_response.json"],
                }
            ]
        },
    )
    _write(repo / "evidence" / "security" / "incident_response.json", {"status": "PASS"})

    monkeypatch.setattr(recent_incident_firebreak_gate, "ROOT", repo)
    monkeypatch.setattr(recent_incident_firebreak_gate, "POLICY", policy)
    monkeypatch.setattr(recent_incident_firebreak_gate, "evidence_root", lambda: repo / "evidence")
    assert (
        recent_incident_firebreak_gate.main(["--changed-files", "tooling/security/recent_incident_firebreak_gate.py"]) == 0
    )


def test_recent_incident_firebreak_gate_fails_when_required_check_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "recent_incident_firebreak_policy.json"
    _write(
        policy,
        {
            "active_incidents": [
                {
                    "incident_id": "INC-2",
                    "affected_paths": [".github/workflows"],
                    "required_reports": ["post_incident_closure_gate.json"],
                }
            ]
        },
    )

    monkeypatch.setattr(recent_incident_firebreak_gate, "ROOT", repo)
    monkeypatch.setattr(recent_incident_firebreak_gate, "POLICY", policy)
    monkeypatch.setattr(recent_incident_firebreak_gate, "evidence_root", lambda: repo / "evidence")
    assert recent_incident_firebreak_gate.main(["--changed-files", ".github/workflows/ci.yml"]) == 1
    report = json.loads((repo / "evidence" / "security" / "recent_incident_firebreak_gate.json").read_text(encoding="utf-8"))
    assert "firebreak_required_check_not_pass:INC-2:post_incident_closure_gate.json:MISSING" in report["findings"]
