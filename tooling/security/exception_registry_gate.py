#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy
from tooling.security.report_io import write_json_report

REQUIRED = ["id", "ticket", "owner", "reason", "expires_at_utc", "created_at_utc"]


def _parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


ROOT = Path(__file__).resolve().parents[2]


def _reason_text(item: dict[str, object]) -> str:
    reason = str(item.get("reason", "")).strip()
    if reason:
        return reason
    return str(item.get("justification", "")).strip()


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

    historical_raw = payload.get("closed_exceptions", []) if isinstance(payload, dict) else []
    historical = [item for item in historical_raw if isinstance(item, dict)] if isinstance(historical_raw, list) else []
    by_id: dict[str, dict[str, object]] = {}
    for item in [*historical, *entries]:
        exception_id = str(item.get("id", "")).strip()
        if exception_id and exception_id not in by_id:
            by_id[exception_id] = item

    renewal_checks = 0
    renewal_failures = 0

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

        renewal_of = str(
            item.get("renewal_of", "")
            or item.get("renews_exception_id", "")
            or item.get("supersedes_exception_id", "")
            or item.get("supersedes_id", "")
        ).strip()
        if not renewal_of:
            continue

        renewal_checks += 1
        previous = by_id.get(renewal_of)
        if previous is None:
            renewal_failures += 1
            findings.append(f"renewal_references_unknown_exception:{ix}:{renewal_of}")
            continue

        approval_signature = str(item.get("approval_signature", "")).strip()
        if not approval_signature:
            renewal_failures += 1
            findings.append(f"renewal_missing_approval_signature:{ix}")

        prior_signature = str(previous.get("approval_signature", "")).strip()
        if approval_signature and prior_signature and approval_signature == prior_signature:
            renewal_failures += 1
            findings.append(f"renewal_reuses_approval_signature:{ix}:{renewal_of}")

        if _reason_text(item).casefold() == _reason_text(previous).casefold():
            renewal_failures += 1
            findings.append(f"renewal_reason_delta_missing:{ix}:{renewal_of}")

    max_active = int(policy.get("max_active_exceptions", 3))
    if active > max_active:
        findings.append(f"active_exceptions_exceed_limit:{active}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "active_exceptions": active,
            "max_active_exceptions": max_active,
            "renewal_checks": renewal_checks,
            "renewal_failures": renewal_failures,
        },
        "metadata": {"gate": "exception_registry_gate", "registry": str(path.relative_to(ROOT)).replace("\\", "/")},
    }
    out = evidence_root() / "security" / "exception_registry_gate.json"
    write_json_report(out, report)
    print(f"EXCEPTION_REGISTRY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
