"""Run lightweight Glyphser runtime benchmarks and emit JSON evidence."""

from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService
from runtime.glyphser.registry.interface_hash import compute_interface_hash

ROOT = Path(__file__).resolve().parents[2]

AUTH_MARKER = "auth-marker"

OUT = ROOT / "evidence" / "benchmarks" / "latest.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _time_call(fn, repeats: int = 1000) -> dict[str, float]:
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
    return {
        "avg_ms": round(statistics.mean(samples), 6),
        "p95_ms": round(statistics.quantiles(samples, n=100)[94], 6),
        "min_ms": round(min(samples), 6),
        "max_ms": round(max(samples), 6),
    }


def run() -> dict[str, object]:
    tmp_dir = ROOT / "artifacts" / "generated" / "benchmarks"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    class _NoAuditRuntimeApiService(RuntimeApiService):
        # Keep benchmark focused on runtime operations, not log growth overhead.
        def _audit(
            self,
            operation: str,
            token: str,
            job_id: str,
            scope: str,
            replay_verdict: str = "",
        ) -> None:
            return None

    service = _NoAuditRuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_dir / "runtime-state.json",
            audit_log_path=tmp_dir / "runtime-audit.log.jsonl",
        )
    )

    registry = {
        "registry_schema_version": "1.0.0",
        "operator_records": [
            {
                "operator_id": "Glyphser.Model.Forward",
                "version": "1.0.0",
                "method": "POST",
            },
            {
                "operator_id": "Glyphser.Trace.TraceSidecar",
                "version": "1.0.0",
                "method": "POST",
            },
        ],
    }

    interface_hash_metrics = _time_call(lambda: compute_interface_hash(registry), repeats=5000)

    first = service.submit_job(
        payload={"bench": True, "step": 1},
        token=AUTH_MARKER,
        scope="bench",
        idempotency_key="bench-key",
    )
    service.submit_job(
        payload={"bench": True, "step": 1},
        token=AUTH_MARKER,
        scope="bench",
        idempotency_key="bench-key",
    )

    status_metrics = _time_call(
        lambda: service.status(first["job_id"], token=AUTH_MARKER, scope="bench"),
        repeats=2000,
    )
    evidence_metrics = _time_call(
        lambda: service.evidence(first["job_id"], token=AUTH_MARKER, scope="bench"),
        repeats=500,
    )

    return {
        "schema_version": "glyphser-benchmark.v1",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "python": "3.12+",
            "host": "local",
        },
        "benchmarks": {
            "compute_interface_hash": interface_hash_metrics,
            "runtime_status": status_metrics,
            "runtime_evidence": evidence_metrics,
        },
        "notes": [
            "Numbers represent local single-host benchmark timings.",
            "Use this file for trend tracking, not cross-host absolute comparisons.",
        ],
    }


def main() -> int:
    payload = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
