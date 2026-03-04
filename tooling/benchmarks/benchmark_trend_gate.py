#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.quality_gates.telemetry import emit_gate_trace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BASELINE = ROOT / "artifacts" / "expected" / "benchmarks" / "trend_baseline_v0.2.0.json"
LATEST = ROOT / "evidence" / "benchmarks" / "latest.json"
OUT = ROOT / "evidence" / "gates" / "quality" / "benchmark_trend.json"


def _extract(latest: dict, key: str) -> float:
    section, metric = key.split(".", 1)
    return float(latest["benchmarks"][section][metric])


def evaluate() -> dict:
    findings: list[str] = []
    if not BASELINE.exists():
        findings.append("missing_baseline")
    if not LATEST.exists():
        findings.append("missing_latest")

    if findings:
        payload = {"status": "FAIL", "findings": findings}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(ROOT, "benchmark_trend", payload)
        return payload

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    latest = json.loads(LATEST.read_text(encoding="utf-8"))

    factor = float(baseline.get("max_regression_factor", 2.0))
    checks = []
    for key, base_val in baseline.get("metrics", {}).items():
        actual = _extract(latest, key)
        threshold = float(base_val) * factor
        checks.append(
            {
                "metric": key,
                "baseline": float(base_val),
                "threshold": threshold,
                "actual": actual,
            }
        )
        if actual > threshold:
            findings.append(f"trend_regression:{key}:{actual:.6f}>{threshold:.6f}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checks": checks,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "benchmark_trend", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("BENCHMARK_TREND_GATE: PASS")
        return 0
    print("BENCHMARK_TREND_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
