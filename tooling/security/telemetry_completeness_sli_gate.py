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
POLICY = ROOT / "governance" / "security" / "security_observability_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY)
    telemetry = policy.get("telemetry_completeness", {})
    if not isinstance(telemetry, dict):
        telemetry = {}
    required_fields = telemetry.get("required_fields", [])
    if not isinstance(required_fields, list):
        required_fields = []
    required = [str(x).strip() for x in required_fields if isinstance(x, str) and str(x).strip()]
    threshold = float(telemetry.get("required_fields_present_rate_threshold", 1.0))

    events_path = evidence_root() / "security" / "security_events.jsonl"
    total_events = 0
    present = 0
    total = 0
    findings: list[str] = []

    if not events_path.exists():
        findings.append("missing_security_events")
    else:
        for idx, raw in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw.strip():
                continue
            total_events += 1
            try:
                event = json.loads(raw)
            except Exception:
                findings.append(f"invalid_json_line:{idx}")
                continue
            if not isinstance(event, dict):
                findings.append(f"invalid_event_object:{idx}")
                continue
            for field in required:
                total += 1
                if str(event.get(field, "")).strip():
                    present += 1

    rate = (present / total) if total else 1.0
    if rate < threshold:
        findings.append(f"telemetry_completeness_below_threshold:{rate:.4f}<{threshold:.4f}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_fields": required,
            "required_fields_present_rate": rate,
            "required_fields_present_rate_threshold": threshold,
            "events_checked": total_events,
        },
        "metadata": {"gate": "telemetry_completeness_sli_gate"},
    }
    out = evidence_root() / "security" / "telemetry_completeness_sli_gate.json"
    write_json_report(out, report)
    print(f"TELEMETRY_COMPLETENESS_SLI_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
