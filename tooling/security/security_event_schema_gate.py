#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

SCHEMA = ROOT / "governance" / "security" / "security_event_schema.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = [x for x in schema.get("required_fields", []) if isinstance(x, str)]
    allowed_severities = {x for x in schema.get("allowed_severities", []) if isinstance(x, str)}
    event_type = str(schema.get("event_type", "security_gate_status"))

    events_path = evidence_root() / "security" / "security_events.jsonl"
    security_dir = evidence_root() / "security"
    findings: list[str] = []
    checked = 0
    fail_event_artifact_refs: set[str] = set()
    if events_path.exists():
        for idx, raw in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip():
                continue
            checked += 1
            try:
                event = json.loads(raw)
            except Exception:
                findings.append(f"invalid_json_line:{idx}")
                continue
            if not isinstance(event, dict):
                findings.append(f"invalid_event_object:{idx}")
                continue
            for field in required:
                if not str(event.get(field, "")).strip():
                    findings.append(f"missing_field:{idx}:{field}")
            if str(event.get("event_type", "")) != event_type:
                findings.append(f"invalid_event_type:{idx}")
            sev = str(event.get("severity", ""))
            if sev and sev not in allowed_severities:
                findings.append(f"invalid_severity:{idx}:{sev}")
            if str(event.get("status", "")).upper() == "FAIL":
                artifact_ref = str(event.get("artifact_ref", "")).strip()
                if artifact_ref:
                    fail_event_artifact_refs.add(artifact_ref)

    fail_reports_checked = 0
    fail_reports_without_event = 0
    for report_path in sorted(security_dir.glob("*.json")):
        if report_path.name in {"security_event_export.json", "security_event_schema_gate.json"}:
            continue
        try:
            report_payload = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(report_payload, dict):
            continue
        if str(report_payload.get("status", "")).upper() != "FAIL":
            continue
        fail_reports_checked += 1
        artifact_ref = str(report_path.relative_to(ROOT)).replace("\\", "/")
        if artifact_ref not in fail_event_artifact_refs:
            fail_reports_without_event += 1
            findings.append(f"missing_fail_event_payload:{artifact_ref}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_events": checked,
            "fail_reports_checked": fail_reports_checked,
            "fail_reports_without_event": fail_reports_without_event,
            "required_fields": required,
            "schema": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "security_event_schema_gate"},
    }
    out = evidence_root() / "security" / "security_event_schema_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_EVENT_SCHEMA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
