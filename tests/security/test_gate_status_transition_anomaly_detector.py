from __future__ import annotations

import json
from pathlib import Path

from tooling.security import gate_status_transition_anomaly_detector


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_transition_detector_passes_without_anomaly(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "PASS"})

    monkeypatch.setattr(gate_status_transition_anomaly_detector, "ROOT", repo)
    monkeypatch.setattr(gate_status_transition_anomaly_detector, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        gate_status_transition_anomaly_detector,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "gate_status_transition_history.json",
    )

    assert gate_status_transition_anomaly_detector.main([]) == 0
    report = json.loads((sec / "gate_status_transition_anomaly_detector.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["anomalies_detected"] == 0


def test_transition_detector_warns_for_chronic_non_pass_to_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "PASS"})
    _write(
        sec / "gate_status_transition_history.json",
        {
            "schema_version": 1,
            "history": {
                "gate_a.json": ["WARN", "FAIL", "WARN"],
            },
        },
    )

    monkeypatch.setattr(gate_status_transition_anomaly_detector, "ROOT", repo)
    monkeypatch.setattr(gate_status_transition_anomaly_detector, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        gate_status_transition_anomaly_detector,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "gate_status_transition_history.json",
    )

    assert gate_status_transition_anomaly_detector.main([]) == 0
    report = json.loads((sec / "gate_status_transition_anomaly_detector.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["anomalies_detected"] == 1
    assert any(str(item).startswith("suspicious_recovery_transition:gate_a.json") for item in report["findings"])
