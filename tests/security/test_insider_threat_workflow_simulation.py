from __future__ import annotations

import json
from pathlib import Path

from tooling.security import insider_threat_workflow_simulation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_insider_threat_workflow_simulation_passes_for_expected_detections(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario_file = repo / "governance" / "security" / "insider_threat_workflow_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario_file,
        {
            "scenarios": [
                {
                    "id": "perm",
                    "kind": "permission_widening",
                    "expected_detection": True,
                    "mutated_workflow": "permissions:\n  contents: write\n",
                },
                {
                    "id": "pin",
                    "kind": "pin_removal",
                    "expected_detection": True,
                    "mutated_workflow": "steps:\n  - uses: actions/checkout\n",
                },
                {
                    "id": "bypass",
                    "kind": "gate_bypass",
                    "expected_detection": True,
                    "mutated_workflow": "if: always()\n",
                },
            ]
        },
    )
    monkeypatch.setattr(insider_threat_workflow_simulation, "ROOT", repo)
    monkeypatch.setattr(insider_threat_workflow_simulation, "SCENARIO_PATH", scenario_file)
    monkeypatch.setattr(insider_threat_workflow_simulation, "evidence_root", lambda: repo / "evidence")

    assert insider_threat_workflow_simulation.main([]) == 0
    report = json.loads((sec / "insider_threat_workflow_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["mismatches"] == 0


def test_insider_threat_workflow_simulation_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario_file = repo / "governance" / "security" / "insider_threat_workflow_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario_file,
        {
            "scenarios": [
                {
                    "id": "missed",
                    "kind": "gate_bypass",
                    "expected_detection": True,
                    "mutated_workflow": "if: github.ref == 'refs/heads/main'\n",
                }
            ]
        },
    )
    monkeypatch.setattr(insider_threat_workflow_simulation, "ROOT", repo)
    monkeypatch.setattr(insider_threat_workflow_simulation, "SCENARIO_PATH", scenario_file)
    monkeypatch.setattr(insider_threat_workflow_simulation, "evidence_root", lambda: repo / "evidence")

    assert insider_threat_workflow_simulation.main([]) == 1
    report = json.loads((sec / "insider_threat_workflow_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "simulation_mismatch:missed" in report["findings"]
