#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_TODO = ""
SECTION_RE = re.compile(r"^([A-Z0-9]{1,4})\.\s+")


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        try:
            dt = datetime.fromisoformat(fixed.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


def _collect_counts(todo_path: Path) -> tuple[int, int, int, dict[str, dict[str, int]]]:
    section_counts: dict[str, dict[str, int]] = {"GLOBAL": {"pending": 0, "in_progress": 0, "done": 0}}
    current_section = "GLOBAL"
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
    pending = sum(v["pending"] for v in section_counts.values())
    in_progress = sum(v["in_progress"] for v in section_counts.values())
    done = sum(v["done"] for v in section_counts.values())
    return pending, in_progress, done, section_counts


def _load_history(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    try:
        payload = json.loads(history_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        history = payload.get("history", [])
        if isinstance(history, list):
            return [x for x in history if isinstance(x, dict)]
    return []


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    sec = evidence_root() / "security"
    history_path = sec / "hardening_burndown_history.json"
    dashboard_path = sec / "hardening_burndown_dashboard.json"
    findings: list[str] = []
    skipped = False
    now = _now_utc()

    if not configured or not todo_path.exists():
        skipped = True
        pending = in_progress = done = 0
        section_counts: dict[str, dict[str, int]] = {}
        completion_pct = 100.0
    else:
        pending, in_progress, done, section_counts = _collect_counts(todo_path)
        total = pending + in_progress + done
        completion_pct = 100.0 if total == 0 else round((done / total) * 100.0, 2)

    snapshot = {
        "timestamp_utc": now.isoformat(),
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "total": pending + in_progress + done,
        "completion_pct": completion_pct,
    }
    history = _load_history(history_path)
    if history and history[-1].get("timestamp_utc") == snapshot["timestamp_utc"]:
        history[-1] = snapshot
    else:
        history.append(snapshot)
    history = history[-365:]

    if len(history) >= 2:
        prev = history[-2]
        delta_pending = int(snapshot["pending"]) - int(prev.get("pending", snapshot["pending"]))
        delta_done = int(snapshot["done"]) - int(prev.get("done", snapshot["done"]))
    else:
        delta_pending = 0
        delta_done = 0

    write_json_report(
        history_path,
        {
            "status": "PASS",
            "findings": [],
            "summary": {"samples": len(history)},
            "metadata": {"gate": "hardening_todo_burndown_dashboard"},
            "history": history,
        },
    )
    report = {
        "status": "PASS" if skipped or not findings else "FAIL",
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "current": snapshot,
            "delta_pending_vs_prev": delta_pending,
            "delta_done_vs_prev": delta_done,
            "history_samples": len(history),
            "section_counts": section_counts,
        },
        "metadata": {"gate": "hardening_todo_burndown_dashboard"},
    }
    write_json_report(dashboard_path, report)
    print(f"HARDENING_TODO_BURNDOWN_DASHBOARD: {report['status']}")
    print(f"Report: {dashboard_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
