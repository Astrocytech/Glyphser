#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

REQUIRED = ["id", "ticket", "owner", "reason", "expires_at_utc", "created_at_utc"]


def _parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    path = ROOT / str(policy.get("exception_registry_path", "governance/security/temporary_exceptions.json"))
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"exceptions": []}
    entries = payload.get("exceptions", []) if isinstance(payload, dict) else []
    now = datetime.now(UTC)
    findings: list[str] = []
    active = 0

    if not isinstance(entries, list):
        findings.append("invalid_exceptions_list")
        entries = []

    for ix, item in enumerate(entries):
        if not isinstance(item, dict):
            findings.append(f"invalid_entry_type:{ix}")
            continue
        for field in REQUIRED:
            if not str(item.get(field, "")).strip():
                findings.append(f"missing_field:{field}:{ix}")
        exp = _parse_ts(str(item.get("expires_at_utc", "")))
        if exp is None:
            findings.append(f"invalid_expiry:{ix}")
            continue
        if exp <= now:
            findings.append(f"expired_exception:{ix}")
        else:
            active += 1

    max_active = int(policy.get("max_active_exceptions", 3))
    if active > max_active:
        findings.append(f"active_exceptions_exceed_limit:{active}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"active_exceptions": active, "max_active_exceptions": max_active},
        "metadata": {"gate": "exception_registry_gate", "registry": str(path.relative_to(ROOT)).replace('\\', '/')},
    }
    out = evidence_root() / "security" / "exception_registry_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EXCEPTION_REGISTRY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
