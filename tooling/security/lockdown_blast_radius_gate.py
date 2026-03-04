#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy


def _parse(ts: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    lockdown_path = ROOT / "governance" / "security" / "emergency_lockdown_policy.json"
    lockdown = json.loads(lockdown_path.read_text(encoding="utf-8")) if lockdown_path.exists() else {}
    if not isinstance(lockdown, dict):
        lockdown = {}

    findings: list[str] = []
    enabled = lockdown.get("lockdown_enabled") is True
    disabled_ops = lockdown.get("disabled_operations", [])
    approved = str(lockdown.get("approved_by", "")).strip()
    expires_raw = str(lockdown.get("expires_at_utc", ""))
    expires = _parse(expires_raw)

    allowed_ops = {x for x in policy.get("lockdown_allowed_operations", []) if isinstance(x, str)}
    if not isinstance(disabled_ops, list):
        findings.append("invalid_disabled_operations")
        disabled_ops = []
    for op in disabled_ops:
        if op not in allowed_ops:
            findings.append(f"operation_outside_blast_radius:{op}")

    if enabled:
        if not approved:
            findings.append("missing_approval")
        if expires is None:
            findings.append("invalid_expiry")
        else:
            minutes = int((expires - datetime.now(UTC)).total_seconds() / 60)
            if minutes < 0:
                findings.append("lockdown_already_expired")
            if minutes > int(policy.get("lockdown_max_duration_minutes", 240)):
                findings.append("lockdown_duration_exceeds_policy")

    rollback = ROOT / str(
        policy.get(
            "rollback_attestation_path",
            "evidence/security/lockdown_rollback_attestation.json",
        )
    )
    if not rollback.exists():
        findings.append("missing_rollback_attestation")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lockdown_enabled": enabled,
            "disabled_operations": disabled_ops,
            "allowed_operations": sorted(allowed_ops),
            "approved_by": approved,
            "expires_at_utc": expires_raw,
        },
        "metadata": {"gate": "lockdown_blast_radius_gate"},
    }
    out = evidence_root() / "security" / "lockdown_blast_radius_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"LOCKDOWN_BLAST_RADIUS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
