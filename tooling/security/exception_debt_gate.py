#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

ROOT = Path(__file__).resolve().parents[2]


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    budget = int(policy.get("exception_debt_budget", 8))
    min_reason_len = int(policy.get("minimum_exception_reason_length", 24))
    now = datetime.now(UTC)
    findings: list[str] = []

    exceptions_path = ROOT / "governance" / "security" / "temporary_exceptions.json"
    ex_payload = json.loads(exceptions_path.read_text(encoding="utf-8")) if exceptions_path.exists() else {"exceptions": []}
    ex_items = ex_payload.get("exceptions", []) if isinstance(ex_payload, dict) else []
    active_ex = 0
    if not isinstance(ex_items, list):
        ex_items = []
        findings.append("invalid_exceptions_list")
    for idx, item in enumerate(ex_items):
        if not isinstance(item, dict):
            findings.append(f"invalid_exception_entry:{idx}")
            continue
        owner = str(item.get("owner", "")).strip()
        reason = str(item.get("reason", "")).strip()
        exp = _parse_ts(str(item.get("expires_at_utc", "")))
        if not owner:
            findings.append(f"owner_missing:exception:{idx}")
        if len(reason) < min_reason_len:
            findings.append(f"justification_too_short:exception:{idx}")
        if exp is None:
            findings.append(f"invalid_expiry:exception:{idx}")
            continue
        if exp > now:
            active_ex += 1
        else:
            findings.append(f"expired_entry:exception:{idx}")

    waivers_path = evidence_root() / "repro" / "waivers.json"
    active_waivers = 0
    if waivers_path.exists():
        try:
            w_payload = json.loads(waivers_path.read_text(encoding="utf-8"))
        except Exception:
            w_payload = {}
            findings.append("invalid_waivers_json")
        waivers = w_payload.get("waivers", []) if isinstance(w_payload, dict) else []
        if not isinstance(waivers, list):
            waivers = []
            findings.append("invalid_waivers_list")
        for idx, item in enumerate(waivers):
            if not isinstance(item, dict):
                findings.append(f"invalid_waiver_entry:{idx}")
                continue
            owner = str(item.get("owner", "")).strip()
            reason = str(item.get("reason", "")).strip()
            exp = _parse_ts(str(item.get("expires_at_utc", "")))
            if not owner:
                findings.append(f"owner_missing:waiver:{idx}")
            if len(reason) < min_reason_len:
                findings.append(f"justification_too_short:waiver:{idx}")
            if exp is None:
                findings.append(f"invalid_expiry:waiver:{idx}")
                continue
            if exp > now:
                active_waivers += 1
            else:
                findings.append(f"expired_entry:waiver:{idx}")

    total_active = active_ex + active_waivers
    if total_active > budget:
        findings.append(f"exception_debt_budget_exceeded:{total_active}:{budget}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "active_exceptions": active_ex,
            "active_waivers": active_waivers,
            "total_active": total_active,
            "exception_debt_budget": budget,
            "minimum_exception_reason_length": min_reason_len,
        },
        "metadata": {"gate": "exception_debt_gate"},
    }
    out = evidence_root() / "security" / "exception_debt_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EXCEPTION_DEBT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
