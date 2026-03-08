from __future__ import annotations

import json
from pathlib import Path

from tooling.benchmarks import benchmark_trend_gate


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_benchmark_trend_gate_passes(tmp_path: Path, monkeypatch):
    baseline = tmp_path / "baseline.json"
    latest = tmp_path / "latest.json"
    out = tmp_path / "trend.json"

    _write_json(
        baseline,
        {
            "schema_version": "glyphser-benchmark-trend-baseline.v1",
            "max_regression_factor": 2.0,
            "metrics": {
                "compute_interface_hash.avg_ms": 0.05,
                "runtime_status.avg_ms": 300.0,
                "runtime_evidence.avg_ms": 700.0,
            },
        },
    )
    _write_json(
        latest,
        {
            "benchmarks": {
                "compute_interface_hash": {"avg_ms": 0.01},
                "runtime_status": {"avg_ms": 100.0},
                "runtime_evidence": {"avg_ms": 200.0},
            }
        },
    )

    monkeypatch.setattr(benchmark_trend_gate, "BASELINE", baseline)
    monkeypatch.setattr(benchmark_trend_gate, "LATEST", latest)
    monkeypatch.setattr(benchmark_trend_gate, "OUT", out)

    report = benchmark_trend_gate.evaluate()
    assert report["status"] == "PASS"
