#!/usr/bin/env python3
"""Compute deterministic parity/divergence metrics without optional ML deps."""

from __future__ import annotations

import contextlib
import io
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash
from tooling.scripts import run_hello_core

OUT = ROOT / "evidence" / "benchmarks" / "variance_impact.json"
FIXTURE_TRACE = ROOT / "artifacts" / "inputs" / "fixtures" / "hello-core" / "trace.json"


def _run_hello_core() -> list[dict]:
    with contextlib.redirect_stdout(io.StringIO()):
        rc = run_hello_core.main()
    if rc != 0:
        raise RuntimeError("hello-core fixture run failed")
    return json.loads(FIXTURE_TRACE.read_text(encoding="utf-8"))


def main() -> int:
    trace_a = _run_hello_core()
    trace_b = _run_hello_core()

    hash_a = compute_trace_hash(trace_a)
    hash_b = compute_trace_hash(trace_b)

    # Synthetic divergence check by mutating one trace record.
    mutated = list(trace_a)
    mutated[-1] = dict(mutated[-1])
    mutated[-1]["operator_id"] = "Glyphser.Model.ModelIR_Executor_MUTATED"
    hash_mutated = compute_trace_hash(mutated)

    payload = {
        "schema_version": "glyphser-variance-impact.v1",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "same_seed_match": hash_a == hash_b,
        "different_seed_diverges": hash_a != hash_mutated,
        "trace_hash_run_a": hash_a,
        "trace_hash_run_b": hash_b,
        "trace_hash_mutated": hash_mutated,
        "adoption_signal": "PASS" if (hash_a == hash_b and hash_a != hash_mutated) else "FAIL",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
