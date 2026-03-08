from __future__ import annotations

import json
from pathlib import Path

from tooling.security import strict_lane_fail_closed_control_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_strict_lane_fail_closed_control_gate_passes_with_unconditional_controls(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {
            "schema_version": 1,
            "mandatory_workflows": [
                ".github/workflows/ci.yml",
                ".github/workflows/security-maintenance.yml",
                ".github/workflows/release.yml",
            ],
            "required_controls": ["python tooling/security/policy_signature_gate.py --strict-key"],
        },
    )
    for rel in ("ci.yml", "security-maintenance.yml", "release.yml"):
        _write(
            repo / ".github" / "workflows" / rel,
            """
jobs:
  gate:
    steps:
      - name: policy
        run: python tooling/security/policy_signature_gate.py --strict-key
""".strip()
            + "\n",
        )

    monkeypatch.setattr(strict_lane_fail_closed_control_gate, "ROOT", repo)
    monkeypatch.setattr(
        strict_lane_fail_closed_control_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
    )
    monkeypatch.setattr(strict_lane_fail_closed_control_gate, "evidence_root", lambda: ev)

    assert strict_lane_fail_closed_control_gate.main([]) == 0
    report = json.loads((ev / "security" / "strict_lane_fail_closed_control_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_strict_lane_fail_closed_control_gate_fails_when_controls_are_masked(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {
            "schema_version": 1,
            "mandatory_workflows": [
                ".github/workflows/ci.yml",
                ".github/workflows/security-maintenance.yml",
                ".github/workflows/release.yml",
            ],
            "required_controls": ["python tooling/security/policy_signature_gate.py --strict-key"],
        },
    )
    for rel in ("ci.yml", "security-maintenance.yml", "release.yml"):
        _write(
            repo / ".github" / "workflows" / rel,
            """
jobs:
  gate:
    steps:
      - name: policy
        continue-on-error: true
        run: python tooling/security/policy_signature_gate.py --strict-key || true
""".strip()
            + "\n",
        )

    monkeypatch.setattr(strict_lane_fail_closed_control_gate, "ROOT", repo)
    monkeypatch.setattr(
        strict_lane_fail_closed_control_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
    )
    monkeypatch.setattr(strict_lane_fail_closed_control_gate, "evidence_root", lambda: ev)

    assert strict_lane_fail_closed_control_gate.main([]) == 1
    report = json.loads((ev / "security" / "strict_lane_fail_closed_control_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("fail_open_control_continue_on_error:") for item in report["findings"])
    assert any(item.startswith("missing_fail_closed_control:") for item in report["findings"])
