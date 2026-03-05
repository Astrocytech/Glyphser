#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "critical_control_backup_policy.json"


def _report_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    controls_summary: list[dict[str, str]] = []

    policy_payload = json.loads(POLICY.read_text(encoding="utf-8"))
    controls = policy_payload.get("controls", []) if isinstance(policy_payload, dict) else []
    if not isinstance(controls, list):
        raise ValueError("backup verifier policy controls must be a list")

    sec = evidence_root() / "security"
    for control in controls:
        if not isinstance(control, dict):
            findings.append("invalid_control_entry")
            continue
        control_id = str(control.get("control_id", "")).strip()
        primary_name = str(control.get("primary_report", "")).strip()
        backup_names = control.get("backup_reports", [])
        fail_closed = bool(control.get("fail_closed", True))
        if not control_id or not primary_name or not isinstance(backup_names, list):
            findings.append(f"invalid_control_config:{control_id or 'unknown'}")
            continue

        primary_status = _report_status(sec / primary_name)
        backup_statuses = {name: _report_status(sec / str(name)) for name in backup_names}
        passing_backup = next((name for name, status in backup_statuses.items() if status == "PASS"), None)

        control_outcome = "PASS"
        if primary_status == "PASS":
            control_outcome = "PASS"
        elif primary_status == "FAIL" and fail_closed:
            control_outcome = "FAIL"
            findings.append(f"primary_failed_fail_closed:{control_id}:{primary_name}")
        elif primary_status in {"MISSING", "INVALID", "UNKNOWN"}:
            if passing_backup:
                findings.append(f"backup_verifier_used:{control_id}:{passing_backup}")
            else:
                control_outcome = "FAIL"
                findings.append(f"control_unavailable_no_backup:{control_id}:{primary_name}")
        elif primary_status == "FAIL":
            if passing_backup:
                findings.append(f"fail_open_backup_used:{control_id}:{passing_backup}")
            else:
                control_outcome = "FAIL"
                findings.append(f"primary_failed_no_backup:{control_id}:{primary_name}")
        else:
            control_outcome = "FAIL"
            findings.append(f"unknown_primary_status:{control_id}:{primary_status}")

        controls_summary.append(
            {
                "control_id": control_id,
                "primary_report": primary_name,
                "primary_status": primary_status,
                "selected_backup": passing_backup or "",
                "outcome": control_outcome,
            }
        )

    any_fail = any(item.get("outcome") == "FAIL" for item in controls_summary)
    report = {
        "status": "FAIL" if any_fail else "PASS",
        "findings": findings,
        "summary": {"controls_evaluated": len(controls_summary), "controls_failed": sum(1 for i in controls_summary if i["outcome"] == "FAIL")},
        "metadata": {"gate": "critical_control_backup_verifier_gate", "controls": controls_summary},
    }
    out = sec / "critical_control_backup_verifier_gate.json"
    write_json_report(out, report)
    print(f"CRITICAL_CONTROL_BACKUP_VERIFIER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
