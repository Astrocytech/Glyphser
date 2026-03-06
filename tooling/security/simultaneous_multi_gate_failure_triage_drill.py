#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DRILL = ROOT / "governance" / "security" / "simultaneous_multi_gate_failure_triage_drill.json"


def _parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _verify_signed_json(path: Path, findings: list[str]) -> dict[str, Any]:
    if not path.exists():
        findings.append("missing_simultaneous_multi_gate_failure_triage_drill")
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    sig_path = path.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append("missing_simultaneous_multi_gate_failure_triage_drill_signature")
    else:
        sig = sig_path.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(path, sig, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(path, sig, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_simultaneous_multi_gate_failure_triage_drill_signature")
    return payload if isinstance(payload, dict) else {}


def _str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = _verify_signed_json(DRILL, findings)

    status = str(payload.get("status", "")).upper()
    if status != "PASS":
        findings.append(f"drill_not_passed:{status or 'MISSING'}")

    incident_id = str(payload.get("incident_id", "")).strip()
    if not incident_id:
        findings.append("missing_incident_id")

    failing_gates = _str_list(payload.get("failing_gates", []))
    if len(failing_gates) < 2:
        findings.append(f"insufficient_simultaneous_failures:{len(failing_gates)}<2")

    triage_started = _parse_ts(str(payload.get("triage_started_at_utc", "")).strip())
    triage_completed = _parse_ts(str(payload.get("triage_completed_at_utc", "")).strip())
    if triage_started is None or triage_completed is None:
        findings.append("invalid_triage_timestamps")
        triage_duration_min = None
    else:
        triage_duration_min = (triage_completed - triage_started).total_seconds() / 60.0
        if triage_duration_min < 0:
            findings.append("negative_triage_duration")

    escalation_path = _str_list(payload.get("escalation_path", []))
    if not escalation_path:
        findings.append("missing_escalation_path")

    remediation_actions = _str_list(payload.get("remediation_actions", []))
    if not remediation_actions:
        findings.append("missing_remediation_actions")

    root_cause = str(payload.get("root_cause", "")).strip()
    if not root_cause:
        findings.append("missing_root_cause")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "incident_id": incident_id,
            "failing_gate_count": len(failing_gates),
            "triage_duration_minutes": triage_duration_min,
            "escalation_hops": len(escalation_path),
            "remediation_actions": len(remediation_actions),
        },
        "metadata": {"gate": "simultaneous_multi_gate_failure_triage_drill"},
    }
    out = evidence_root() / "security" / "simultaneous_multi_gate_failure_triage_drill.json"
    write_json_report(out, report)
    print(f"SIMULTANEOUS_MULTI_GATE_FAILURE_TRIAGE_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
