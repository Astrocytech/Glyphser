from __future__ import annotations

import json
from pathlib import Path

from tooling.security import incident_severity_scoring_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_incident_severity_report_scores_findings(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "FAIL", "findings": ["tamper_detected"]})

    monkeypatch.setattr(incident_severity_scoring_report, "ROOT", repo)
    monkeypatch.setattr(incident_severity_scoring_report, "evidence_root", lambda: repo / "evidence")

    assert incident_severity_scoring_report.main([]) == 0
    report = json.loads((sec / "incident_severity_scoring_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["max_severity_score"] >= 80
    assert report["scored_findings"][0]["severity"] in {"HIGH", "CRITICAL"}


def test_incident_severity_report_passes_without_high_signal(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "PASS", "findings": ["informational advisory"]})

    monkeypatch.setattr(incident_severity_scoring_report, "ROOT", repo)
    monkeypatch.setattr(incident_severity_scoring_report, "evidence_root", lambda: repo / "evidence")

    assert incident_severity_scoring_report.main([]) == 0
    report = json.loads((sec / "incident_severity_scoring_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["critical_or_high_findings"] == 0
