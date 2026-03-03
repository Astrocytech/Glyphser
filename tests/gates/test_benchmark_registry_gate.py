from __future__ import annotations

import json
from pathlib import Path

from tooling.benchmarks import benchmark_registry_gate

ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_benchmark_registry_gate_passes(tmp_path: Path, monkeypatch):
    registry = tmp_path / "registry.json"
    latest = tmp_path / "latest.json"
    variance = tmp_path / "variance.json"
    out = tmp_path / "report.json"

    _write_json(
        registry,
        {
            "schema_version": "glyphser-benchmark-registry.v1",
            "thresholds": {
                "compute_interface_hash_avg_ms_max": 0.1,
                "runtime_status_avg_ms_max": 10.0,
                "runtime_evidence_avg_ms_max": 30.0,
            },
            "determinism_requirements": {
                "same_seed_match": True,
                "different_seed_diverges": True,
            },
        },
    )
    _write_json(
        latest,
        {
            "benchmarks": {
                "compute_interface_hash": {"avg_ms": 0.01},
                "runtime_status": {"avg_ms": 1.0},
                "runtime_evidence": {"avg_ms": 2.0},
            }
        },
    )
    _write_json(variance, {"same_seed_match": True, "different_seed_diverges": True})

    monkeypatch.setattr(benchmark_registry_gate, "REGISTRY", registry)
    monkeypatch.setattr(benchmark_registry_gate, "LATEST", latest)
    monkeypatch.setattr(benchmark_registry_gate, "VARIANCE", variance)
    monkeypatch.setattr(benchmark_registry_gate, "OUT", out)

    report = benchmark_registry_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads(out.read_text(encoding="utf-8"))
    assert emitted["status"] == "PASS"
