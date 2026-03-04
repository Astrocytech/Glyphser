#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]
LOCKDOWN_POLICY = ROOT / "governance" / "security" / "emergency_lockdown_policy.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    sec = evidence_root() / "security"

    lockdown_payload: dict[str, Any] = {}
    if LOCKDOWN_POLICY.exists():
        loaded = json.loads(LOCKDOWN_POLICY.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            lockdown_payload = loaded
    lockdown_enabled = lockdown_payload.get("lockdown_enabled") is True

    containment = sec / "containment_verification.json"
    containment_status = "SKIPPED"
    if lockdown_enabled:
        if not containment.exists():
            findings.append("missing_containment_verification_artifact")
            containment_status = "MISSING"
        else:
            payload = json.loads(containment.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                findings.append("invalid_containment_verification_artifact")
                containment_status = "INVALID"
            else:
                containment_status = str(payload.get("status", "UNKNOWN")).upper()
                if containment_status != "PASS":
                    findings.append(f"containment_verification_not_pass:{containment_status}")
                for field in ("incident_id", "verified_by", "verified_at_utc", "notes"):
                    if not str(payload.get(field, "")).strip():
                        findings.append(f"missing_containment_field:{field}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lockdown_enabled": lockdown_enabled,
            "containment_status": containment_status,
            "containment_path": str(containment.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "containment_verification_gate"},
    }
    out = sec / "containment_verification_gate.json"
    write_json_report(out, report)
    print(f"CONTAINMENT_VERIFICATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
