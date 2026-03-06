#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
PRODUCER_POLICY = ROOT / "governance" / "security" / "report_producer_version_policy.json"


def _is_critical(row: dict[str, Any]) -> bool:
    step_name = str(row.get("step_name", "")).lower()
    command_hash = str(row.get("command_hash_sha256", "")).strip()
    return bool(command_hash) and ("security" in step_name or "gate" in step_name or "drill" in step_name)


def _extract_run_id(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    metadata = report.get("metadata", {})
    for section in (summary, metadata):
        if not isinstance(section, dict):
            continue
        for key in ("run_id", "run_correlation_id"):
            value = str(section.get(key, "")).strip()
            if value:
                return value
    return ""


def _extract_generated_at_utc(report: dict[str, Any]) -> str:
    metadata = report.get("metadata", {})
    if not isinstance(metadata, dict):
        return ""
    value = str(metadata.get("generated_at_utc", "")).strip()
    return value


def _parse_utc(ts: str) -> datetime | None:
    if not ts:
        return None
    fixed = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(fixed)
    except ValueError:
        return None


def _producer_major(version: str) -> int | None:
    head = version.split(".", 1)[0].strip()
    if not head.isdigit():
        return None
    return int(head)


def _supported_producer_majors() -> set[int]:
    if not PRODUCER_POLICY.exists():
        return {1}
    try:
        payload = json.loads(PRODUCER_POLICY.read_text(encoding="utf-8"))
    except Exception:
        return {1}
    if not isinstance(payload, dict):
        return {1}
    majors = payload.get("supported_major_versions", [])
    if not isinstance(majors, list):
        return {1}
    out = {int(item) for item in majors if isinstance(item, int) and item > 0}
    return out or {1}


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
        run_id = str(row.get("run_correlation_id", "")).strip()
        if not run_id:
            findings.append(f"missing_run_correlation_id:{job}:{idx}")

    sec_dir = evidence_root() / "security"
    run_id_by_report: dict[str, str] = {}
    timestamp_rows: list[tuple[float, str, datetime]] = []
    supported_majors = _supported_producer_majors()
    for report_path in sorted(sec_dir.glob("*.json")):
        if report_path.name == "security_run_correlation_id_gate.json":
            continue
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        run_id = _extract_run_id(payload)
        if run_id:
            run_id_by_report[report_path.name] = run_id
        metadata = payload.get("metadata", {})
        if isinstance(payload.get("status"), str):
            producer_version = ""
            if isinstance(metadata, dict):
                producer_version = str(metadata.get("producer_version", "")).strip()
            if not producer_version:
                findings.append(f"missing_report_producer_version:{report_path.name}")
            else:
                major = _producer_major(producer_version)
                if major is None:
                    findings.append(f"invalid_report_producer_version:{report_path.name}:{producer_version}")
                elif major not in supported_majors:
                    findings.append(f"incompatible_report_producer_version:{report_path.name}:{producer_version}")
        generated = _extract_generated_at_utc(payload)
        parsed_generated = _parse_utc(generated)
        if generated and parsed_generated is None:
            findings.append(f"invalid_report_generated_at_utc:{report_path.name}")
        if parsed_generated is not None:
            timestamp_rows.append((report_path.stat().st_mtime_ns / 1_000_000_000, report_path.name, parsed_generated))
    shared_run_ids = sorted(set(run_id_by_report.values()))
    if len(shared_run_ids) > 1:
        findings.append(f"inconsistent_run_id_across_reports:{','.join(shared_run_ids)}")
    if len(timestamp_rows) >= 2:
        ordered = sorted(timestamp_rows, key=lambda item: (item[0], item[1]))
        previous_name = ordered[0][1]
        previous_ts = ordered[0][2]
        for _, name, ts in ordered[1:]:
            if ts < previous_ts:
                findings.append(f"non_monotonic_report_timestamps:{previous_name}->{name}")
            previous_name = name
            previous_ts = ts

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "critical_steps_checked": len(critical_rows),
            "total_steps_seen": len(rows),
            "reports_with_run_id": len(run_id_by_report),
            "shared_run_ids": shared_run_ids,
            "reports_with_generated_at_utc": len(timestamp_rows),
            "supported_producer_major_versions": sorted(supported_majors),
        },
        "metadata": {"gate": "security_run_correlation_id_gate"},
    }
    out = evidence_root() / "security" / "security_run_correlation_id_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_RUN_CORRELATION_ID_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
