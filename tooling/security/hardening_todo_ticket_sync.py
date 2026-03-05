#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_TODO = ""
TICKET_RE = re.compile(r"\bticket:\s*([A-Za-z][A-Za-z0-9]+-\d+)\b", re.IGNORECASE)
OWNER_RE = re.compile(r"\bowner:\s*([A-Za-z0-9_.@/\-]+)", re.IGNORECASE)
ITEM_RE = re.compile(r"^\[(?P<state>[ x~])\]\s*(?P<text>.+)$")


def _load_ticket_state(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in payload.items():
        if isinstance(key, str) and isinstance(value, str):
            out[key.upper()] = value.upper()
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export ticket mapping and coverage for hardening TODO items.")
    parser.add_argument("--ticket-state-file", default="", help="Optional JSON map: {\"SEC-123\": \"OPEN|DONE|...\"}")
    args = parser.parse_args([] if argv is None else argv)

    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    ticket_state_file = Path(args.ticket_state_file).expanduser() if args.ticket_state_file else None
    ticket_states = _load_ticket_state(ticket_state_file)

    skipped = False
    findings: list[str] = []
    items_without_ticket = 0
    items_without_owner = 0
    mapped_items: list[dict[str, Any]] = []

    if not configured or not todo_path.exists():
        skipped = True
    else:
        for idx, raw in enumerate(todo_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = raw.strip()
            match = ITEM_RE.match(stripped)
            if not match:
                continue
            text = match.group("text").strip()
            if not text:
                continue
            ticket_match = TICKET_RE.search(text)
            owner_match = OWNER_RE.search(text)
            ticket_id = ticket_match.group(1).upper() if ticket_match else ""
            owner = owner_match.group(1) if owner_match else ""
            if not ticket_id:
                items_without_ticket += 1
            if not owner:
                items_without_owner += 1
            mapped_items.append(
                {
                    "line": idx,
                    "state": match.group("state"),
                    "ticket_id": ticket_id,
                    "ticket_state": ticket_states.get(ticket_id, ""),
                    "owner": owner,
                    "text": text,
                }
            )

    if items_without_ticket > 0:
        findings.append(f"todo_items_missing_ticket_id:{items_without_ticket}")
    if items_without_owner > 0:
        findings.append(f"todo_items_missing_owner:{items_without_owner}")

    open_items = sum(1 for item in mapped_items if item["state"] != "x")
    closed_ticket_items = sum(1 for item in mapped_items if item["ticket_state"] in {"DONE", "CLOSED", "RESOLVED"})
    drift_items = sum(
        1
        for item in mapped_items
        if item["state"] != "x" and item["ticket_state"] in {"DONE", "CLOSED", "RESOLVED"}
    )
    if drift_items > 0:
        findings.append(f"todo_ticket_state_drift:{drift_items}")

    report = {
        "status": "PASS" if skipped or not findings else "FAIL",
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "ticket_state_file": str(ticket_state_file) if ticket_state_file else "",
            "total_todo_items": len(mapped_items),
            "open_todo_items": open_items,
            "todo_items_missing_ticket_id": items_without_ticket,
            "todo_items_missing_owner": items_without_owner,
            "todo_ticket_state_drift": drift_items,
            "closed_ticket_items": closed_ticket_items,
        },
        "metadata": {"gate": "hardening_todo_ticket_sync"},
        "items": mapped_items[:500],
    }
    out = evidence_root() / "security" / "hardening_todo_ticket_sync.json"
    write_json_report(out, report)
    print(f"HARDENING_TODO_TICKET_SYNC: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
