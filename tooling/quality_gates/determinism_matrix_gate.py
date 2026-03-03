#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash
from tooling.scripts import run_hello_core

OUT = ROOT / "evidence" / "gates" / "quality" / "determinism_matrix.json"
FIXTURE_TRACE = ROOT / "artifacts" / "inputs" / "fixtures" / "hello-core" / "trace.json"
GOLDEN = ROOT / "specs" / "examples" / "hello-core" / "hello-core-golden.json"


def evaluate() -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        rc = run_hello_core.main()

    findings: list[str] = []
    actual_trace = ""
    expected_trace = ""

    if rc != 0:
        findings.append("hello_core_run_failed")
    if not FIXTURE_TRACE.exists():
        findings.append("missing_trace_file")
    if not GOLDEN.exists():
        findings.append("missing_golden_file")

    if not findings:
        trace_records = json.loads(FIXTURE_TRACE.read_text(encoding="utf-8"))
        actual_trace = compute_trace_hash(trace_records)
        expected_trace = json.loads(GOLDEN.read_text(encoding="utf-8"))["expected_identities"]["trace_final_hash"]
        if actual_trace != expected_trace:
            findings.append("trace_hash_mismatch")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "expected_trace_hash": expected_trace,
        "actual_trace_hash": actual_trace,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("DETERMINISM_MATRIX_GATE: PASS")
        return 0
    print("DETERMINISM_MATRIX_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
