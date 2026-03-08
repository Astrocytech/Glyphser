from __future__ import annotations

import json
from pathlib import Path

from tooling.security import containment_auto_trigger_recommendations


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_containment_recommendations_pass_without_severe_findings(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "PASS", "findings": []})

    monkeypatch.setattr(containment_auto_trigger_recommendations, "ROOT", repo)
    monkeypatch.setattr(containment_auto_trigger_recommendations, "evidence_root", lambda: repo / "evidence")

    assert containment_auto_trigger_recommendations.main([]) == 0
    report = json.loads((sec / "containment_auto_trigger_recommendations.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["severe_signals"] == 0


def test_containment_recommendations_warn_for_severe_findings(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "FAIL", "findings": ["policy_signature_tamper_detected"]})

    monkeypatch.setattr(containment_auto_trigger_recommendations, "ROOT", repo)
    monkeypatch.setattr(containment_auto_trigger_recommendations, "evidence_root", lambda: repo / "evidence")

    assert containment_auto_trigger_recommendations.main([]) == 0
    report = json.loads((sec / "containment_auto_trigger_recommendations.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["severe_signals"] == 1
    assert report["recommendations"]
    assert any(str(item).startswith("severe_signal_detected:gate_a.json:policy_signature_tamper_detected") for item in report["findings"])
