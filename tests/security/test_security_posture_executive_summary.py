from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_posture_executive_summary


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def test_security_posture_executive_summary_passes_with_verifiable_references(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    for name in (
        "security_super_gate.json",
        "security_verification_summary.json",
        "security_pipeline_reliability_dashboard.json",
        "security_dashboard.json",
    ):
        _write_json(sec / name, {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})

    monkeypatch.setattr(security_posture_executive_summary, "ROOT", repo)
    monkeypatch.setattr(security_posture_executive_summary, "evidence_root", lambda: repo / "evidence")
    assert security_posture_executive_summary.main([]) == 0

    report = json.loads((sec / "security_posture_executive_summary.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["resolved_artifact_count"] == 4
    assert report["summary"]["machine_verifiable_reference_digest"].startswith("sha256:")
    assert all(str(item.get("sha256", "")).startswith("sha256:") for item in report["references"])
    board = json.loads((sec / "security_board_posture_summary.json").read_text(encoding="utf-8"))
    assert board["metadata"]["audience"] == "board"


def test_security_posture_executive_summary_fails_when_required_artifact_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(sec / "security_super_gate.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_json(
        sec / "security_verification_summary.json",
        {"status": "PASS", "findings": [], "summary": {}, "metadata": {}},
    )
    _write_json(
        sec / "security_pipeline_reliability_dashboard.json",
        {"status": "PASS", "findings": [], "summary": {}, "metadata": {}},
    )

    monkeypatch.setattr(security_posture_executive_summary, "ROOT", repo)
    monkeypatch.setattr(security_posture_executive_summary, "evidence_root", lambda: repo / "evidence")
    assert security_posture_executive_summary.main([]) == 1

    report = json.loads((sec / "security_posture_executive_summary.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_required_artifact:security_dashboard:") for item in report["findings"])
