#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _is_critical(row: dict[str, Any]) -> bool:
    command_hash = str(row.get("command_hash_sha256", "")).strip()
    step_name = str(row.get("step_name", "")).lower()
    return bool(command_hash) and ("security" in step_name or "gate" in step_name or "drill" in step_name)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    source = evidence_root() / "security" / "security_step_execution_fingerprint.json"
    if not source.exists():
        findings.append("missing_security_step_execution_fingerprint_report")
        rows: list[dict[str, Any]] = []
    else:
        payload = json.loads(source.read_text(encoding="utf-8"))
        raw_rows = payload.get("fingerprints", []) if isinstance(payload, dict) else []
        rows = [row for row in raw_rows if isinstance(row, dict)]

    critical_rows = [row for row in rows if _is_critical(row)]
    if not critical_rows:
        findings.append("no_critical_steps_found")

    for row in critical_rows:
        job = str(row.get("job", "")).strip() or "unknown-job"
        idx = str(row.get("step_index", "unknown-index")).strip()
        start_marker = str(row.get("start_marker", "")).strip()
        end_marker = str(row.get("end_marker", "")).strip()
        if not start_marker or not start_marker.startswith("STEP_START:"):
            findings.append(f"missing_step_start_marker:{job}:{idx}")
        if not end_marker or not end_marker.startswith("STEP_END:"):
            findings.append(f"missing_step_end_marker:{job}:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "critical_steps_checked": len(critical_rows),
            "total_steps_seen": len(rows),
        },
        "metadata": {"gate": "security_step_traceability_marker_gate"},
    }
    out = evidence_root() / "security" / "security_step_traceability_marker_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_STEP_TRACEABILITY_MARKER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
