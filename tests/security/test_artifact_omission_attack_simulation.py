from __future__ import annotations

import json
from pathlib import Path

from tooling.security import artifact_omission_attack_simulation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_artifact_omission_attack_simulation_passes_for_expected_cases(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario = repo / "governance" / "security" / "artifact_omission_attack_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario,
        {
            "scenarios": [
                {
                    "id": "missing",
                    "expected_detection": True,
                    "expected_artifacts": ["a.json", "b.json"],
                    "produced_artifacts": ["a.json"],
                },
                {
                    "id": "complete",
                    "expected_detection": False,
                    "expected_artifacts": ["a.json"],
                    "produced_artifacts": ["a.json"],
                },
            ]
        },
    )
    monkeypatch.setattr(artifact_omission_attack_simulation, "ROOT", repo)
    monkeypatch.setattr(artifact_omission_attack_simulation, "SCENARIO_PATH", scenario)
    monkeypatch.setattr(artifact_omission_attack_simulation, "evidence_root", lambda: repo / "evidence")

    assert artifact_omission_attack_simulation.main([]) == 0
    report = json.loads((sec / "artifact_omission_attack_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["mismatches"] == 0


def test_artifact_omission_attack_simulation_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario = repo / "governance" / "security" / "artifact_omission_attack_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario,
        {
            "scenarios": [
                {
                    "id": "unexpected-pass",
                    "expected_detection": False,
                    "expected_artifacts": ["a.json", "b.json"],
                    "produced_artifacts": ["a.json"],
                }
            ]
        },
    )
    monkeypatch.setattr(artifact_omission_attack_simulation, "ROOT", repo)
    monkeypatch.setattr(artifact_omission_attack_simulation, "SCENARIO_PATH", scenario)
    monkeypatch.setattr(artifact_omission_attack_simulation, "evidence_root", lambda: repo / "evidence")

    assert artifact_omission_attack_simulation.main([]) == 1
    report = json.loads((sec / "artifact_omission_attack_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("artifact_omission_simulation_mismatch:unexpected-pass:") for item in report["findings"])
