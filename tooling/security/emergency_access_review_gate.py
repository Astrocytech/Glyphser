#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "emergency_access_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_utc(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_emergency_access_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    grants_rel = str(policy.get("grants_path", "governance/security/emergency_access_grants.json")).strip()
    grants_path = ROOT / grants_rel if grants_rel else Path("")
    max_active_days = int(policy.get("max_active_days", 7) or 7)

    if not grants_rel or not grants_path.exists():
        findings.append("missing_emergency_access_grants")
        grants: list[dict[str, Any]] = []
    else:
        payload = _load_json(grants_path)
        raw = payload.get("grants", []) if isinstance(payload, dict) else []
        grants = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    now = datetime.now(UTC)
    active_count = 0

    for item in grants:
        grant_id = str(item.get("id", "")).strip() or "unknown"
        status = str(item.get("status", "active")).strip().lower() or "active"
        granted_at = _parse_utc(str(item.get("granted_at_utc", "")))
        expires_at = _parse_utc(str(item.get("expires_at_utc", "")))

        if status == "active":
            active_count += 1
            if expires_at is None:
                findings.append(f"active_grant_missing_expiry:{grant_id}")
            elif expires_at < now:
                findings.append(f"active_grant_expired:{grant_id}")
            if granted_at is not None and granted_at + timedelta(days=max_active_days) < now:
                findings.append(f"active_grant_exceeds_max_duration:{grant_id}")
        elif status == "closed":
            closure = item.get("closure_attestation", {})
            if not isinstance(closure, dict):
                closure = {}
            if not str(closure.get("ticket", "")).strip():
                findings.append(f"closed_grant_missing_closure_ticket:{grant_id}")
            if _parse_utc(str(closure.get("closed_at_utc", ""))) is None:
                findings.append(f"closed_grant_missing_closed_at_utc:{grant_id}")
            if not str(closure.get("approved_by", "")).strip():
                findings.append(f"closed_grant_missing_approved_by:{grant_id}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "grants_path": grants_rel,
            "total_grants": len(grants),
            "active_grants": active_count,
            "max_active_days": max_active_days,
        },
        "metadata": {"gate": "emergency_access_review_gate"},
    }
    out = evidence_root() / "security" / "emergency_access_review_gate.json"
    write_json_report(out, report)
    print(f"EMERGENCY_ACCESS_REVIEW_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
