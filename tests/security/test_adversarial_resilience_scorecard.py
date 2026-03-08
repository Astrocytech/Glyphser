from __future__ import annotations

import json
from pathlib import Path

from tooling.security import adversarial_resilience_scorecard


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_adversarial_resilience_scorecard_passes_with_event_history(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    history = repo / "governance" / "security" / "adversarial_detection_history.json"
    sec.mkdir(parents=True)
    _write(
        history,
        {
            "events": [
                {"detection_latency_minutes": 10, "containment_quality_score": 4.0},
                {"detection_latency_minutes": 20, "containment_quality_score": 3.0},
            ]
        },
    )
    monkeypatch.setattr(adversarial_resilience_scorecard, "ROOT", repo)
    monkeypatch.setattr(adversarial_resilience_scorecard, "HISTORY_PATH", history)
    monkeypatch.setattr(adversarial_resilience_scorecard, "evidence_root", lambda: repo / "evidence")

    assert adversarial_resilience_scorecard.main([]) == 0
    report = json.loads((sec / "adversarial_resilience_scorecard.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["mean_detection_latency_minutes"] == 15.0
    assert report["summary"]["mean_containment_quality_score"] == 3.5


def test_adversarial_resilience_scorecard_fails_without_events(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    history = repo / "governance" / "security" / "adversarial_detection_history.json"
    sec.mkdir(parents=True)
    _write(history, {"events": []})
    monkeypatch.setattr(adversarial_resilience_scorecard, "ROOT", repo)
    monkeypatch.setattr(adversarial_resilience_scorecard, "HISTORY_PATH", history)
    monkeypatch.setattr(adversarial_resilience_scorecard, "evidence_root", lambda: repo / "evidence")

    assert adversarial_resilience_scorecard.main([]) == 1
    report = json.loads((sec / "adversarial_resilience_scorecard.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "no_adversarial_detection_events" in report["findings"]
