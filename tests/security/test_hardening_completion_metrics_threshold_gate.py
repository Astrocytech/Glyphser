from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_completion_metrics_threshold_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_completion_metrics_threshold_gate_passes_without_breach(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    thresholds = repo / "governance" / "security" / "hardening_metrics_thresholds.json"
    metrics = repo / "evidence" / "security" / "hardening_completion_metrics.json"
    _write_json(
        thresholds,
        {
            "thresholds": {
                "pending_item_count": {"max": 10},
                "hardening_throughput": {"min": 2},
            }
        },
    )
    _write_json(
        metrics,
        {
            "metrics": {
                "pending_item_count": {"value": 3},
                "hardening_throughput": {"value": 5},
            }
        },
    )

    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "THRESHOLDS", thresholds)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "METRICS", metrics)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "evidence_root", lambda: repo / "evidence")

    assert hardening_completion_metrics_threshold_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics_threshold_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["breaches"] == []


def test_hardening_completion_metrics_threshold_gate_warns_on_breach(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    thresholds = repo / "governance" / "security" / "hardening_metrics_thresholds.json"
    metrics = repo / "evidence" / "security" / "hardening_completion_metrics.json"
    _write_json(
        thresholds,
        {
            "thresholds": {
                "regression_reopen_rate": {"max": 0.1, "severity": "warning"},
            }
        },
    )
    _write_json(
        metrics,
        {
            "metrics": {
                "regression_reopen_rate": {"value": 0.5},
            }
        },
    )

    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "THRESHOLDS", thresholds)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "METRICS", metrics)
    monkeypatch.setattr(hardening_completion_metrics_threshold_gate, "evidence_root", lambda: repo / "evidence")

    assert hardening_completion_metrics_threshold_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics_threshold_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["breaches"] == 1
    assert report["breaches"][0]["metric"] == "regression_reopen_rate"
