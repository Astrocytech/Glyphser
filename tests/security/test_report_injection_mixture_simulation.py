from __future__ import annotations

import json
from pathlib import Path

from tooling.security import report_injection_mixture_simulation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_report_injection_mixture_simulation_passes_for_expected_inputs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario = repo / "governance" / "security" / "report_injection_mixture_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario,
        {
            "scenarios": [
                {
                    "id": "good",
                    "expected_detection": False,
                    "report": {"source": "trusted", "signature_valid": True, "schema_valid": True},
                },
                {
                    "id": "bad",
                    "expected_detection": True,
                    "report": {"source": "fork-pr", "signature_valid": False, "schema_valid": True},
                },
            ]
        },
    )
    monkeypatch.setattr(report_injection_mixture_simulation, "ROOT", repo)
    monkeypatch.setattr(report_injection_mixture_simulation, "SCENARIO_PATH", scenario)
    monkeypatch.setattr(report_injection_mixture_simulation, "evidence_root", lambda: repo / "evidence")

    assert report_injection_mixture_simulation.main([]) == 0
    report = json.loads((sec / "report_injection_mixture_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_report_injection_mixture_simulation_fails_on_expected_detection_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    scenario = repo / "governance" / "security" / "report_injection_mixture_simulation.json"
    sec.mkdir(parents=True)
    _write(
        scenario,
        {
            "scenarios": [
                {
                    "id": "mismatch",
                    "expected_detection": False,
                    "report": {"source": "untrusted", "signature_valid": False, "schema_valid": True},
                }
            ]
        },
    )
    monkeypatch.setattr(report_injection_mixture_simulation, "ROOT", repo)
    monkeypatch.setattr(report_injection_mixture_simulation, "SCENARIO_PATH", scenario)
    monkeypatch.setattr(report_injection_mixture_simulation, "evidence_root", lambda: repo / "evidence")

    assert report_injection_mixture_simulation.main([]) == 1
    report = json.loads((sec / "report_injection_mixture_simulation.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "report_injection_simulation_mismatch:mismatch" in report["findings"]
