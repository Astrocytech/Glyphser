#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        parsed = _parse_ts(fixed)
        if parsed is not None:
            return parsed
    return datetime.now(UTC)


def _load_tickets(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_ticket_registry"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_ticket_registry_json"
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)], ""
    if isinstance(payload, dict):
        raw = payload.get("tickets", [])
        if isinstance(raw, list):
            return [x for x in raw if isinstance(x, dict)], ""
    return [], "invalid_ticket_registry_schema"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    now = _now_utc()
    stale_days = int(os.environ.get("GLYPHSER_HARDENING_STALE_TICKET_GRACE_DAYS", "0") or "0")
    ticket_path = os.environ.get(
        "GLYPHSER_HARDENING_TICKET_STATE_PATH",
        str(ROOT / "governance" / "security" / "hardening_ticket_registry.json"),
    ).strip()
    registry = Path(ticket_path).expanduser()

    tickets, registry_error = _load_tickets(registry)
    findings: list[str] = []
    stale_entries: list[dict[str, Any]] = []
    stale_cutoff = now.timestamp() - (stale_days * 86400)
    if registry_error:
        findings.append(registry_error)

    for idx, row in enumerate(tickets):
        ticket_id = str(row.get("ticket_id", "")).strip().upper()
        state = str(row.get("state", "OPEN")).strip().upper()
        due_at = _parse_ts(row.get("due_at_utc"))
        if not ticket_id:
            findings.append(f"missing_ticket_id:{idx}")
            continue
        if state in {"DONE", "CLOSED", "RESOLVED"}:
            continue
        if due_at is None:
            findings.append(f"missing_or_invalid_due_at_utc:{ticket_id}")
            continue
        if due_at.timestamp() < stale_cutoff:
            days_overdue = int((now - due_at).total_seconds() // 86400)
            stale_entries.append(
                {
                    "ticket_id": ticket_id,
                    "owner": str(row.get("owner", "")).strip(),
                    "state": state,
                    "due_at_utc": due_at.isoformat(),
                    "days_overdue": days_overdue,
                }
            )
            findings.append(f"stale_ticket:{ticket_id}:{days_overdue}d")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "ticket_registry_path": str(registry),
            "total_tickets": len(tickets),
            "stale_tickets": len(stale_entries),
            "stale_ticket_grace_days": stale_days,
        },
        "metadata": {"gate": "hardening_stale_ticket_gate"},
        "stale_entries": stale_entries[:500],
    }
    out = evidence_root() / "security" / "hardening_stale_ticket_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_STALE_TICKET_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
