#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_TODO = ""
SECTION_RE = re.compile(r"^([A-Z0-9]{1,4})\.\s+")
TRIGGER_RE = re.compile(r"\b(trigger|incident|audit|run[-_ ]id)\b", re.IGNORECASE)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    findings: list[str] = []
    status = "PASS"
    skipped = False
    pending_count = 0
    pending_without_trigger = 0
    done_marker_present = False
    section_counts: dict[str, dict[str, int]] = {}
    require_trigger_ref = os.environ.get("GLYPHSER_HARDENING_TODO_REQUIRE_TRIGGER_REF", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if not configured or not todo_path.exists():
        skipped = True
    else:
        text = todo_path.read_text(encoding="utf-8")
        done_marker_present = "DONE" in text
        current_section = "GLOBAL"
        section_counts.setdefault(current_section, {"pending": 0, "in_progress": 0, "done": 0})
        for line in text.splitlines():
            match = SECTION_RE.match(line.strip())
            if match:
                current_section = match.group(1)
                section_counts.setdefault(current_section, {"pending": 0, "in_progress": 0, "done": 0})
                continue
            stripped = line.strip()
            if stripped.startswith("[ ]"):
                pending_count += 1
                section_counts[current_section]["pending"] += 1
                if require_trigger_ref and not TRIGGER_RE.search(stripped):
                    pending_without_trigger += 1
            elif stripped.startswith("[~]"):
                section_counts[current_section]["in_progress"] += 1
            elif stripped.startswith("[x]"):
                section_counts[current_section]["done"] += 1
        if done_marker_present and pending_count > 0:
            status = "FAIL"
            findings.append("done_marker_present_with_pending_items")
        if pending_without_trigger > 0:
            status = "FAIL"
            findings.append("pending_item_missing_trigger_reference")

    report = {
        "status": status,
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "pending_items": pending_count,
            "pending_without_trigger_reference": pending_without_trigger,
            "done_marker_present": done_marker_present,
            "section_counts": section_counts,
            "require_trigger_reference": require_trigger_ref,
        },
        "metadata": {"gate": "hardening_todo_consistency_gate"},
    }
    out = evidence_root() / "security" / "hardening_todo_consistency_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_TODO_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
