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
ADVERSARIAL_HISTORY = ROOT / "governance" / "security" / "adversarial_detection_history.json"
INCIDENT_CATALOG = ROOT / "governance" / "security" / "incident_regression_catalog.json"

SECTION_RE = re.compile(r"^(?P<section>[A-Z]{1,2})(?:\d+)?\.\s*(?P<title>.+)$")
ITEM_RE = re.compile(r"^\[(?P<state>[ x~])\]\s*(?P<text>.+)$")


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _read_todo_sections(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    sections: list[dict[str, Any]] = []
    todo_fingerprint_set: set[str] = set()
    current: dict[str, Any] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        sec = SECTION_RE.match(line)
        if sec:
            current = {"section": sec.group("section"), "title": sec.group("title"), "items": []}
            sections.append(current)
            continue
        itm = ITEM_RE.match(line)
        if not itm or current is None:
            continue
        text = itm.group("text").strip()
        current["items"].append({"state": itm.group("state"), "text": text})
        todo_fingerprint_set.add(_normalize(text))
    return sections, todo_fingerprint_set


def _completed_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for section in sections:
        items = section.get("items", [])
        if not isinstance(items, list) or not items:
            continue
        states = {str(item.get("state", "")) for item in items if isinstance(item, dict)}
        if states == {"x"}:
            out.append(section)
    return out


def _seed_candidates(todo_fingerprints: set[str]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    history = _load_json(ADVERSARIAL_HISTORY) if ADVERSARIAL_HISTORY.exists() else {}
    catalog = _load_json(INCIDENT_CATALOG) if INCIDENT_CATALOG.exists() else {}

    for event in history.get("events", []) if isinstance(history.get("events"), list) else []:
        if not isinstance(event, dict):
            continue
        scenario_id = str(event.get("scenario_id", "")).strip()
        if not scenario_id:
            continue
        title = f"Risk from adversarial scenario: {scenario_id}"
        if _normalize(title) in todo_fingerprints:
            continue
        candidates.append({"source": "adversarial_detection_history", "reference": scenario_id, "title": title})

    for incident in catalog.get("incidents", []) if isinstance(catalog.get("incidents"), list) else []:
        if not isinstance(incident, dict):
            continue
        incident_id = str(incident.get("incident_id", "")).strip()
        if not incident_id:
            continue
        title = f"Risk from incident regression: {incident_id}"
        if _normalize(title) in todo_fingerprints:
            continue
        candidates.append({"source": "incident_regression_catalog", "reference": incident_id, "title": title})

    unique: dict[str, dict[str, str]] = {}
    for row in candidates:
        key = _normalize(row["title"])
        unique[key] = row
    return list(unique.values())


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not TODO_PATH.exists():
        findings.append("missing_hardening_todo")
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"completed_sections": 0, "seeded_net_new_risks": 0},
            "metadata": {"process": "annual_hardening_reset_process"},
        }
        out = evidence_root() / "security" / "annual_hardening_reset_process.json"
        write_json_report(out, report)
        print(f"ANNUAL_HARDENING_RESET_PROCESS: {report['status']}")
        print(f"Report: {out}")
        return 1

    sections, todo_fingerprints = _read_todo_sections(TODO_PATH)
    archived_sections = _completed_sections(sections)
    seeded_risks = _seed_candidates(todo_fingerprints)

    archive_payload = {
        "status": "PASS",
        "sections": archived_sections,
        "summary": {"archived_sections": len(archived_sections)},
    }
    archive_out = evidence_root() / "security" / "annual_hardening_archive.json"
    write_json_report(archive_out, archive_payload)

    seed_payload = {
        "status": "PASS",
        "seeded_risks": seeded_risks,
        "summary": {"seeded_net_new_risks": len(seeded_risks)},
    }
    seed_out = evidence_root() / "security" / "annual_hardening_seed_risks.json"
    write_json_report(seed_out, seed_payload)

    process_report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "completed_sections": len(archived_sections),
            "seeded_net_new_risks": len(seeded_risks),
            "archive_path": str(archive_out),
            "seed_path": str(seed_out),
        },
        "metadata": {"process": "annual_hardening_reset_process"},
    }
    out = evidence_root() / "security" / "annual_hardening_reset_process.json"
    write_json_report(out, process_report)
    print(f"ANNUAL_HARDENING_RESET_PROCESS: {process_report['status']}")
    print(f"Report: {out}")
    return 0 if process_report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
