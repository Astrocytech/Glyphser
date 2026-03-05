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
OWNER_RE = re.compile(r"\bowner:\s*([A-Za-z0-9_.@/\-]+)", re.IGNORECASE)
MILESTONE_RE = re.compile(r"\bmilestone:\s*([A-Za-z0-9_.\-]+)", re.IGNORECASE)
RISK_RE = re.compile(r"\b(?:risk(?:_acceptance)?|risk-ticket|waiver|exception):\s*([A-Za-z0-9_.:/#\-]+)", re.IGNORECASE)
DEFERRED_RE = re.compile(r"\b(defer(?:red)?|postpone(?:d)?|risk accepted|accepted risk)\b", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"\b(?:code|test|tests|workflow|evidence|gate|pr|commit):\s*\S+", re.IGNORECASE)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", DEFAULT_TODO).strip()
    todo_path = Path(configured).expanduser() if configured else Path("")
    findings: list[str] = []
    status = "PASS"
    skipped = False
    pending_count = 0
    pending_without_trigger = 0
    in_progress_missing_owner = 0
    in_progress_missing_milestone = 0
    deferred_missing_risk_acceptance = 0
    done_missing_evidence_link = 0
    done_marker_present = False
    section_counts: dict[str, dict[str, int]] = {}
    require_trigger_ref = os.environ.get("GLYPHSER_HARDENING_TODO_REQUIRE_TRIGGER_REF", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    require_owner_milestone = os.environ.get("GLYPHSER_HARDENING_TODO_REQUIRE_OWNER_MILESTONE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    require_risk_acceptance = os.environ.get("GLYPHSER_HARDENING_TODO_REQUIRE_RISK_ACCEPTANCE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    require_done_evidence_link = os.environ.get("GLYPHSER_HARDENING_TODO_REQUIRE_DONE_EVIDENCE_LINK", "").strip().lower() in {
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
                if require_risk_acceptance and DEFERRED_RE.search(stripped) and not RISK_RE.search(stripped):
                    deferred_missing_risk_acceptance += 1
            elif stripped.startswith("[~]"):
                section_counts[current_section]["in_progress"] += 1
                if require_owner_milestone:
                    if not OWNER_RE.search(stripped):
                        in_progress_missing_owner += 1
                    if not MILESTONE_RE.search(stripped):
                        in_progress_missing_milestone += 1
            elif stripped.startswith("[x]"):
                section_counts[current_section]["done"] += 1
                if require_done_evidence_link and not EVIDENCE_RE.search(stripped):
                    done_missing_evidence_link += 1
        if done_marker_present and pending_count > 0:
            status = "FAIL"
            findings.append("done_marker_present_with_pending_items")
        if pending_without_trigger > 0:
            status = "FAIL"
            findings.append("pending_item_missing_trigger_reference")
        if in_progress_missing_owner > 0:
            status = "FAIL"
            findings.append("in_progress_item_missing_owner")
        if in_progress_missing_milestone > 0:
            status = "FAIL"
            findings.append("in_progress_item_missing_milestone")
        if deferred_missing_risk_acceptance > 0:
            status = "FAIL"
            findings.append("deferred_item_missing_risk_acceptance")
        if done_missing_evidence_link > 0:
            status = "FAIL"
            findings.append("done_item_missing_evidence_link")

    report = {
        "status": status,
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "pending_items": pending_count,
            "pending_without_trigger_reference": pending_without_trigger,
            "in_progress_missing_owner": in_progress_missing_owner,
            "in_progress_missing_milestone": in_progress_missing_milestone,
            "deferred_missing_risk_acceptance": deferred_missing_risk_acceptance,
            "done_missing_evidence_link": done_missing_evidence_link,
            "done_marker_present": done_marker_present,
            "section_counts": section_counts,
            "require_trigger_reference": require_trigger_ref,
            "require_owner_milestone": require_owner_milestone,
            "require_risk_acceptance": require_risk_acceptance,
            "require_done_evidence_link": require_done_evidence_link,
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
