#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.quality_gates.telemetry import emit_gate_trace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTRY = ROOT / "artifacts" / "expected" / "benchmarks" / "registry.json"
LATEST = ROOT / "evidence" / "benchmarks" / "latest.json"
VARIANCE = ROOT / "evidence" / "benchmarks" / "variance_impact.json"
OUT = ROOT / "evidence" / "gates" / "quality" / "benchmark_registry.json"


def evaluate() -> dict:
    findings: list[str] = []
    if not REGISTRY.exists():
        findings.append("missing_registry")
    if not LATEST.exists():
        findings.append("missing_latest_benchmark")
    if not VARIANCE.exists():
        findings.append("missing_variance_benchmark")

    if findings:
        payload = {"status": "FAIL", "findings": findings}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(ROOT, "benchmark_registry", payload)
        return payload

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    latest = json.loads(LATEST.read_text(encoding="utf-8"))
    variance = json.loads(VARIANCE.read_text(encoding="utf-8"))

    th = registry.get("thresholds", {})
    det = registry.get("determinism_requirements", {})

    cih = latest["benchmarks"]["compute_interface_hash"]["avg_ms"]
    sts = latest["benchmarks"]["runtime_status"]["avg_ms"]
    evd = latest["benchmarks"]["runtime_evidence"]["avg_ms"]

    if cih > float(th.get("compute_interface_hash_avg_ms_max", 0.1)):
        findings.append("compute_interface_hash_avg_ms_exceeded")
    if sts > float(th.get("runtime_status_avg_ms_max", 10.0)):
        findings.append("runtime_status_avg_ms_exceeded")
    if evd > float(th.get("runtime_evidence_avg_ms_max", 30.0)):
        findings.append("runtime_evidence_avg_ms_exceeded")

    if bool(variance.get("same_seed_match")) != bool(det.get("same_seed_match", True)):
        findings.append("same_seed_match_requirement_failed")
    if bool(variance.get("different_seed_diverges")) != bool(det.get("different_seed_diverges", True)):
        findings.append("different_seed_diverges_requirement_failed")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "metrics": {
            "compute_interface_hash_avg_ms": cih,
            "runtime_status_avg_ms": sts,
            "runtime_evidence_avg_ms": evd,
        },
        "determinism": {
            "same_seed_match": bool(variance.get("same_seed_match")),
            "different_seed_diverges": bool(variance.get("different_seed_diverges")),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "benchmark_registry", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("BENCHMARK_REGISTRY_GATE: PASS")
        return 0
    print("BENCHMARK_REGISTRY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
