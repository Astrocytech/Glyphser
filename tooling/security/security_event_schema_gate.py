#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "governance" / "security" / "security_event_schema.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = [x for x in schema.get("required_fields", []) if isinstance(x, str)]
    allowed_severities = {x for x in schema.get("allowed_severities", []) if isinstance(x, str)}
    event_type = str(schema.get("event_type", "security_gate_status"))

    events_path = evidence_root() / "security" / "security_events.jsonl"
    findings: list[str] = []
    checked = 0
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

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_events": checked,
            "required_fields": required,
            "schema": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "security_event_schema_gate"},
    }
    out = evidence_root() / "security" / "security_event_schema_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_EVENT_SCHEMA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
