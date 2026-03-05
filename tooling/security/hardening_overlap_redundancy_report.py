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

TODO_PATH = ROOT / "glyphser_security_hardening_master_todo.txt"
SECTION_RE = re.compile(r"^(?P<section>[A-Z]{1,2})(?:\d+)?\.\s")
ITEM_RE = re.compile(r"^\[(?: |x|~)\]\s*(?P<text>.+)$")


def _normalize(text: str) -> str:
    cleaned = re.sub(r"`[^`]+`", "", text.lower())
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _section_in_scope(section: str) -> bool:
    if section == "AA":
        return True
    if len(section) == 1 and "A" <= section <= "Z":
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    overlaps: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}

    if not TODO_PATH.exists():
        findings.append("missing_hardening_todo")
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"items_scanned": 0, "overlap_groups": 0},
            "metadata": {"report": "hardening_overlap_redundancy_report"},
            "overlaps": overlaps,
        }
        out = evidence_root() / "security" / "hardening_overlap_redundancy_report.json"
        write_json_report(out, report)
        print(f"HARDENING_OVERLAP_REDUNDANCY_REPORT: {report['status']}")
        print(f"Report: {out}")
        return 1

    current_section = ""
    items_scanned = 0
    for lineno, raw in enumerate(TODO_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        sec_match = SECTION_RE.match(line)
        if sec_match:
            current_section = sec_match.group("section")
            continue
        item_match = ITEM_RE.match(line)
        if not item_match:
            continue
        if not _section_in_scope(current_section):
            continue
        text = item_match.group("text").strip()
        norm = _normalize(text)
        if not norm:
            continue
        items_scanned += 1
        grouped.setdefault(norm, []).append({"section": current_section, "line": lineno, "text": text})

    for norm, entries in grouped.items():
        sections = {item["section"] for item in entries}
        if len(entries) > 1 and len(sections) > 1:
            overlaps.append(
                {
                    "fingerprint": norm,
                    "sections": sorted(sections),
                    "entries": entries,
                }
            )

    report = {
        "status": "PASS",
        "findings": findings,
        "summary": {
            "items_scanned": items_scanned,
            "overlap_groups": len(overlaps),
            "overlapping_items": sum(len(group["entries"]) for group in overlaps),
        },
        "metadata": {"report": "hardening_overlap_redundancy_report", "scope": "A..AA"},
        "overlaps": overlaps[:500],
    }
    out = evidence_root() / "security" / "hardening_overlap_redundancy_report.json"
    write_json_report(out, report)
    print(f"HARDENING_OVERLAP_REDUNDANCY_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
