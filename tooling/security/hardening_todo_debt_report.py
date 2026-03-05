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


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    max_pending = int(os.environ.get("GLYPHSER_HARDENING_MAX_PENDING", "0") or "0")

    findings: list[str] = []
    skipped = False
    section_counts: dict[str, dict[str, int]] = {}

    if not configured or not todo_path.exists():
        skipped = True
    else:
        current_section = "GLOBAL"
        section_counts.setdefault(current_section, {"pending": 0, "in_progress": 0, "done": 0})
        for line in todo_path.read_text(encoding="utf-8").splitlines():
            match = SECTION_RE.match(line.strip())
            if match:
                current_section = match.group(1)
                section_counts.setdefault(current_section, {"pending": 0, "in_progress": 0, "done": 0})
                continue
            stripped = line.strip()
            if stripped.startswith("[ ]"):
                section_counts[current_section]["pending"] += 1
            elif stripped.startswith("[~]"):
                section_counts[current_section]["in_progress"] += 1
            elif stripped.startswith("[x]"):
                section_counts[current_section]["done"] += 1

    total_pending = sum(v["pending"] for v in section_counts.values())
    total_in_progress = sum(v["in_progress"] for v in section_counts.values())
    total_done = sum(v["done"] for v in section_counts.values())
    total_items = total_pending + total_in_progress + total_done
    completion_pct = 100.0 if total_items == 0 else round((total_done / total_items) * 100.0, 2)

    if max_pending > 0 and total_pending > max_pending:
        findings.append(f"pending_budget_exceeded:{total_pending}:{max_pending}")

    top_pending_sections = sorted(
        (
            {"section": k, "pending": v["pending"], "in_progress": v["in_progress"], "done": v["done"]}
            for k, v in section_counts.items()
            if v["pending"] > 0
        ),
        key=lambda row: row["pending"],
        reverse=True,
    )[:20]

    report = {
        "status": "PASS" if skipped or not findings else "FAIL",
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "total_pending": total_pending,
            "total_in_progress": total_in_progress,
            "total_done": total_done,
            "total_items": total_items,
            "completion_pct": completion_pct,
            "pending_budget": max_pending,
            "top_pending_sections": top_pending_sections,
            "section_counts": section_counts,
        },
        "metadata": {"gate": "hardening_todo_debt_report"},
    }
    out = evidence_root() / "security" / "hardening_todo_debt_report.json"
    write_json_report(out, report)
    print(f"HARDENING_TODO_DEBT_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
