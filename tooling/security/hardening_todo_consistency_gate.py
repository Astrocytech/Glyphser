#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

DEFAULT_TODO = ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    findings: list[str] = []
    status = "PASS"
    skipped = False
    pending_count = 0
    done_marker_present = False

    if not configured or not todo_path.exists():
        skipped = True
    else:
        text = todo_path.read_text(encoding="utf-8")
        done_marker_present = "DONE" in text
        pending_count = sum(1 for line in text.splitlines() if line.strip().startswith("[ ]"))
        if done_marker_present and pending_count > 0:
            status = "FAIL"
            findings.append("done_marker_present_with_pending_items")

    report = {
        "status": status,
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path),
            "pending_items": pending_count,
            "done_marker_present": done_marker_present,
        },
        "metadata": {"gate": "hardening_todo_consistency_gate"},
    }
    out = evidence_root() / "security" / "hardening_todo_consistency_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"HARDENING_TODO_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
