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
ITEM_RE = re.compile(r"^\[(?P<state>[ x~])\]\s*(?P<text>.+)$")
ADD_GATE_RE = re.compile(r"^Add\s+(.+?)\s+gate\b", re.IGNORECASE)


def _gate_stem_from_text(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return f"{normalized}_gate" if normalized else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    strict = os.environ.get("GLYPHSER_HARDENING_TODO_DRIFT_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}
    findings: list[str] = []
    skipped = False
    implemented_but_unchecked = 0
    checked_but_missing = 0
    examined_gate_like_items = 0

    available_gates = {p.stem for p in (ROOT / "tooling" / "security").glob("*_gate.py")}
    if not configured or not todo_path.exists():
        skipped = True
    else:
        for idx, raw in enumerate(todo_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            match = ITEM_RE.match(line)
            if not match:
                continue
            add_gate = ADD_GATE_RE.match(match.group("text").strip())
            if not add_gate:
                continue
            examined_gate_like_items += 1
            stem = _gate_stem_from_text(add_gate.group(1))
            if not stem:
                continue
            has_impl = stem in available_gates
            state = match.group("state")
            if state == " " and has_impl:
                implemented_but_unchecked += 1
                findings.append(f"implemented_but_unchecked:line:{idx}:{stem}")
            if state == "x" and not has_impl:
                checked_but_missing += 1
                findings.append(f"checked_but_missing_implementation:line:{idx}:{stem}")

    status = "PASS"
    if strict and findings:
        status = "FAIL"
    report = {
        "status": status,
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "strict_mode": strict,
            "available_gate_files": len(available_gates),
            "examined_gate_like_items": examined_gate_like_items,
            "implemented_but_unchecked": implemented_but_unchecked,
            "checked_but_missing_implementation": checked_but_missing,
        },
        "metadata": {"gate": "hardening_todo_drift_gate"},
    }
    out = evidence_root() / "security" / "hardening_todo_drift_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_TODO_DRIFT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
