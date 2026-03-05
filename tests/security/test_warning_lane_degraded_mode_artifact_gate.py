from __future__ import annotations

import json
from pathlib import Path

from tooling.security import warning_lane_degraded_mode_artifact_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_warning_lane_degraded_mode_artifact_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {
            "schema_version": 1,
            "mandatory_workflows": [".github/workflows/ci.yml"],
            "required_controls": [],
        },
    )
    _write(
        repo / ".github/workflows/ci.yml",
        """
jobs:
  lane:
    steps:
      - name: waiver
        run: python tooling/security/temporary_waiver_gate.py
      - name: degraded evidence
        run: python tooling/security/degraded_mode_evidence.py
      - name: upload
        run: echo degraded_mode_evidence.json
""".strip()
        + "\n",
    )
    monkeypatch.setattr(warning_lane_degraded_mode_artifact_gate, "ROOT", repo)
    monkeypatch.setattr(
        warning_lane_degraded_mode_artifact_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
    )
    monkeypatch.setattr(warning_lane_degraded_mode_artifact_gate, "evidence_root", lambda: ev)
    assert warning_lane_degraded_mode_artifact_gate.main([]) == 0
    report = json.loads((ev / "security" / "warning_lane_degraded_mode_artifact_gate.json").read_text("utf-8"))
    assert report["status"] == "PASS"


def test_warning_lane_degraded_mode_artifact_gate_fails_when_missing_degraded_mode_step(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {
            "schema_version": 1,
            "mandatory_workflows": [".github/workflows/ci.yml"],
            "required_controls": [],
        },
    )
    _write(
        repo / ".github/workflows/ci.yml",
        """
jobs:
  lane:
    steps:
      - name: rollout
        run: python tooling/security/live_rollout_gate.py --allow-dry-run --allow-missing
""".strip()
        + "\n",
    )
    monkeypatch.setattr(warning_lane_degraded_mode_artifact_gate, "ROOT", repo)
    monkeypatch.setattr(
        warning_lane_degraded_mode_artifact_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
    )
    monkeypatch.setattr(warning_lane_degraded_mode_artifact_gate, "evidence_root", lambda: ev)
    assert warning_lane_degraded_mode_artifact_gate.main([]) == 1
    report = json.loads((ev / "security" / "warning_lane_degraded_mode_artifact_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "warning_lane_missing_degraded_mode_command:.github/workflows/ci.yml" in report["findings"]
    assert "warning_lane_missing_degraded_mode_artifact:.github/workflows/ci.yml" in report["findings"]
