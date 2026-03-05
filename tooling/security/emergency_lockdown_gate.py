#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _parse(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = ROOT / "governance" / "security" / "emergency_lockdown_policy.json"
    sig = policy.with_suffix(policy.suffix + ".sig")
    findings: list[str] = []
    payload = json.loads(policy.read_text(encoding="utf-8")) if policy.exists() else {}
    if not isinstance(payload, dict):
        payload = {}
        findings.append("invalid_lockdown_policy")
    if not sig.exists():
        findings.append("missing_lockdown_policy_signature")
    else:
        s = sig.read_text(encoding="utf-8").strip()
        if not s or not verify_file(policy, s, key=current_key(strict=False)):
            findings.append("lockdown_policy_signature_mismatch")

    enabled = payload.get("lockdown_enabled") is True
    override_policy = payload.get("override_policy", {})
    if not isinstance(override_policy, dict):
        override_policy = {}
    required_distinct_approvals = int(override_policy.get("required_distinct_approvals", 2))
    max_override_duration_hours = float(override_policy.get("max_override_duration_hours", 24))
    expires = _parse(str(payload.get("expires_at_utc", "")))
    updated_at = _parse(str(payload.get("updated_at_utc", "")))
    raw_approvals = payload.get("approved_by", [])
    if isinstance(raw_approvals, str):
        approvals = [x.strip() for x in raw_approvals.split(",") if x.strip()]
    elif isinstance(raw_approvals, list):
        approvals = [str(x).strip() for x in raw_approvals if str(x).strip()]
    else:
        approvals = []
    distinct_approvals = sorted({name.lower() for name in approvals})
    if enabled:
        if len(distinct_approvals) < required_distinct_approvals:
            findings.append("lockdown_missing_approval")
        if expires is None:
            findings.append("lockdown_missing_or_invalid_expiry")
        elif expires <= datetime.now(UTC):
            findings.append("lockdown_expired")
        elif updated_at and (expires - updated_at).total_seconds() > max_override_duration_hours * 3600:
            findings.append("lockdown_expiry_exceeds_max_duration")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lockdown_enabled": enabled,
            "expires_at_utc": payload.get("expires_at_utc", ""),
            "updated_at_utc": payload.get("updated_at_utc", ""),
            "required_distinct_approvals": required_distinct_approvals,
            "distinct_approvals": distinct_approvals,
            "max_override_duration_hours": max_override_duration_hours,
        },
        "metadata": {"gate": "emergency_lockdown_gate"},
    }
    out = evidence_root() / "security" / "emergency_lockdown_gate.json"
    write_json_report(out, report)
    print(f"EMERGENCY_LOCKDOWN_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
