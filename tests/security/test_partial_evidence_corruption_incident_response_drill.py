from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import partial_evidence_corruption_incident_response_drill


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_partial_evidence_corruption_incident_response_drill_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "partial_evidence_corruption_incident_response_drill.json"
    _write(
        drill,
        {
            "status": "PASS",
            "incident_id": "INC-1",
            "corrupted_artifacts": ["evidence/security/a.json"],
            "detection_method": "hash mismatch",
            "containment_actions": ["quarantine evidence root"],
            "recovery_steps": ["restore from archive"],
            "fallback_verification_completed": True,
        },
    )
    _sign(drill)

    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "ROOT", repo)
    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "DRILL", drill)
    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "evidence_root", lambda: repo / "evidence")
    assert partial_evidence_corruption_incident_response_drill.main([]) == 0


def test_partial_evidence_corruption_incident_response_drill_fails_on_missing_requirements(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "partial_evidence_corruption_incident_response_drill.json"
    _write(
        drill,
        {
            "status": "FAIL",
            "incident_id": "",
            "corrupted_artifacts": [],
            "detection_method": "",
            "containment_actions": [],
            "recovery_steps": [],
            "fallback_verification_completed": False,
        },
    )
    _sign(drill)

    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "ROOT", repo)
    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "DRILL", drill)
    monkeypatch.setattr(partial_evidence_corruption_incident_response_drill, "evidence_root", lambda: repo / "evidence")
    assert partial_evidence_corruption_incident_response_drill.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "partial_evidence_corruption_incident_response_drill.json").read_text(
            encoding="utf-8"
        )
    )
    assert "missing_corrupted_artifacts" in report["findings"]
    assert "fallback_verification_not_completed" in report["findings"]
