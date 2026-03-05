#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"
SECTION_RE = re.compile(r"^(?P<section>[A-Z]{1,2}\d*)\.\s+")
PENDING_RE = re.compile(r"^\[\s\]\s+(?P<text>.+)$")
ID_RE = re.compile(r"^SEC-HARD-(\d{4,})$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _fingerprint(section: str, text: str, ordinal: int) -> str:
    material = f"{section}|{ordinal}|{text}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()[:16]


def _next_id(existing_ids: set[str], start: int = 1) -> str:
    value = start
    while True:
        candidate = f"SEC-HARD-{value:04d}"
        if candidate not in existing_ids:
            return candidate
        value += 1


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not TODO.exists():
        findings.append("missing_hardening_todo")
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"pending_items": 0, "registry_entries": 0},
            "metadata": {"process": "hardening_pending_item_registry_sync"},
        }
        out = evidence_root() / "security" / "hardening_pending_item_registry_sync.json"
        write_json_report(out, report)
        print(f"HARDENING_PENDING_ITEM_REGISTRY_SYNC: {report['status']}")
        print(f"Report: {out}")
        return 1

    existing = _load_json(REGISTRY) if REGISTRY.exists() else {}
    existing_entries = existing.get("entries", []) if isinstance(existing.get("entries"), list) else []
    by_fp: dict[str, dict[str, Any]] = {}
    used_ids: set[str] = set()
    for row in existing_entries:
        if not isinstance(row, dict):
            continue
        fp = str(row.get("fingerprint", "")).strip()
        item_id = str(row.get("id", "")).strip()
        if fp:
            by_fp[fp] = row
        if ID_RE.match(item_id):
            used_ids.add(item_id)

    counts: dict[str, int] = {}
    section = "GLOBAL"
    entries: list[dict[str, Any]] = []
    for lineno, raw in enumerate(TODO.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        sec = SECTION_RE.match(line)
        if sec:
            section = sec.group("section")
            continue
        pending = PENDING_RE.match(line)
        if not pending:
            continue
        text = pending.group("text").strip()
        counts[section] = counts.get(section, 0) + 1
        ordinal = counts[section]
        fp = _fingerprint(section, text, ordinal)
        prev = by_fp.get(fp, {})
        item_id = str(prev.get("id", "")).strip()
        if not ID_RE.match(item_id):
            item_id = _next_id(used_ids)
        used_ids.add(item_id)
        entries.append(
            {
                "id": item_id,
                "fingerprint": fp,
                "section": section,
                "line": lineno,
                "text": text,
                "owner": str(prev.get("owner", "unassigned")),
                "priority": str(prev.get("priority", "P3 opportunistic")),
                "milestone": str(prev.get("milestone", "TBD")),
                "target_date": str(prev.get("target_date", "")),
                "dependencies": list(prev.get("dependencies", []))
                if isinstance(prev.get("dependencies", []), list)
                else [],
                "verification": prev.get("verification", {})
                if isinstance(prev.get("verification", {}), dict)
                else {},
                "evidence_link": str(prev.get("evidence_link", "")),
                "status": str(prev.get("status", "pending")),
                "previous_status": str(prev.get("previous_status", prev.get("status", "pending"))),
                "verification_proof": str(prev.get("verification_proof", "")),
                "code_diff_ref": str(prev.get("code_diff_ref", "")),
                "test_diff_ref": str(prev.get("test_diff_ref", "")),
                "ci_run_ref": str(prev.get("ci_run_ref", "")),
                "negative_test_evidence_ref": str(prev.get("negative_test_evidence_ref", "")),
                "regression_green_runs": _as_int(prev.get("regression_green_runs", 0), 0),
            }
        )

    payload = {
        "schema_version": 1,
        "entries": entries,
        "summary": {
            "pending_items": len(entries),
            "unique_ids": len({entry["id"] for entry in entries}),
        },
    }
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"pending_items": len(entries), "registry_entries": len(entries)},
        "metadata": {"process": "hardening_pending_item_registry_sync"},
    }
    out = evidence_root() / "security" / "hardening_pending_item_registry_sync.json"
    write_json_report(out, report)
    print(f"HARDENING_PENDING_ITEM_REGISTRY_SYNC: {report['status']}")
    print(f"Registry: {REGISTRY}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
