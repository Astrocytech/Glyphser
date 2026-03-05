#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TODO = ROOT / "glyphser_security_hardening_master_todo.txt"
EXCEPTIONS = ROOT / "governance" / "security" / "temporary_exceptions.json"
METRICS_HISTORY = ROOT / "evidence" / "security" / "hardening_completion_metrics_history.json"
POLICY = ROOT / "governance" / "security" / "hardening_terminal_completion_policy.json"
DONE_RE = re.compile(r"^DONE\s*$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _pending_count() -> tuple[int, bool]:
    if not TODO.exists():
        return 0, False
    total = 0
    marker = False
    for raw in TODO.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("[ ]"):
            total += 1
        if DONE_RE.match(line):
            marker = True
    return total, marker


def _active_critical_exceptions() -> list[str]:
    if not EXCEPTIONS.exists():
        return []
    payload = _load_json(EXCEPTIONS)
    raw = payload.get("exceptions", []) if isinstance(payload.get("exceptions", []), list) else []
    active: list[str] = []
    for idx, row in enumerate(raw):
        if not isinstance(row, dict):
            continue
        severity = str(row.get("severity", "")).strip().lower()
        if severity != "critical":
            continue
        status = str(row.get("status", "active")).strip().lower()
        is_active = bool(row.get("active", status not in {"closed", "expired"}))
        if is_active and status not in {"closed", "expired"}:
            active.append(str(row.get("id", f"critical-{idx}")))
    return active


def _last_n_runs_green(required_n: int) -> tuple[bool, int, int]:
    if required_n <= 0:
        return True, 0, 0
    if not METRICS_HISTORY.exists():
        return False, 0, required_n
    payload = _load_json(METRICS_HISTORY)
    raw = payload.get("runs", []) if isinstance(payload.get("runs", []), list) else []
    runs = [item for item in raw if isinstance(item, dict)]
    sample = runs[-required_n:]
    if len(sample) < required_n:
        return False, len(sample), required_n
    greens = sum(1 for row in sample if bool(row.get("ci_security_green")))
    return greens == required_n, greens, required_n


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _load_json(POLICY) if POLICY.exists() else {}
    required_n = int(policy.get("last_n_security_runs_green", 3)) if str(policy.get("last_n_security_runs_green", "")).strip() else 3

    pending_count, done_marker_present = _pending_count()
    if pending_count != 0:
        findings.append(f"pending_items_not_zero:{pending_count}")

    active_critical = _active_critical_exceptions()
    if active_critical:
        findings.append(f"active_critical_exceptions:{'|'.join(active_critical[:20])}")

    runs_green, green_count, required = _last_n_runs_green(required_n)
    if not runs_green:
        findings.append(f"last_n_security_runs_not_green:{green_count}/{required}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "pending_item_count": pending_count,
            "done_marker_present": done_marker_present,
            "active_critical_exceptions": len(active_critical),
            "required_last_n_green": required,
            "last_n_green_count": green_count,
        },
        "metadata": {"validator": "hardening_terminal_completion_validator"},
    }
    out = evidence_root() / "security" / "hardening_terminal_completion_validator.json"
    write_json_report(out, report)
    print(f"HARDENING_TERMINAL_COMPLETION_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
