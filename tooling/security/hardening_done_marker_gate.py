#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_TODO = ROOT / "glyphser_security_hardening_master_todo.txt"
SECTION_RE = re.compile(r"^(?P<section>[A-Z]{1,2}\d*)\.\s+")
PENDING_RE = re.compile(r"^\[\s\]\s+")
DONE_LINE_RE = re.compile(r"^DONE\s*$")
SCOPE_BASE_SECTIONS = {*(chr(code) for code in range(ord("A"), ord("Z") + 1)), "AA", "AB"}
REQUIRED_VALIDATOR_REPORTS = (
    "hardening_terminal_completion_validator.json",
    "hardening_completed_item_proof_audit.json",
    "hardening_trigger_backed_findings_validator.json",
)


def _base_section(token: str) -> str:
    return "".join(ch for ch in token if ch.isalpha()).upper()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    todo_path = Path(os.environ.get("GLYPHSER_HARDENING_TODO_PATH", str(DEFAULT_TODO))).expanduser()
    verification_path = evidence_root() / "security" / "hardening_done_marker_verification.json"

    if not todo_path.exists():
        findings.append("missing_hardening_todo")
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"done_marker_present": False, "pending_in_scope": 0},
            "metadata": {"gate": "hardening_done_marker_gate"},
        }
        out = evidence_root() / "security" / "hardening_done_marker_gate.json"
        write_json_report(out, report)
        print(f"HARDENING_DONE_MARKER_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    done_marker_present = False
    pending_in_scope = 0
    completed_in_scope = 0
    current_base = ""
    for raw in todo_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if DONE_LINE_RE.match(line):
            done_marker_present = True
        sec_match = SECTION_RE.match(line)
        if sec_match:
            current_base = _base_section(sec_match.group("section"))
            continue
        if current_base in SCOPE_BASE_SECTIONS and PENDING_RE.match(line):
            pending_in_scope += 1
        if current_base in SCOPE_BASE_SECTIONS and line.startswith("[x]"):
            completed_in_scope += 1

    ci_green = False
    verification_exists = verification_path.exists()
    verified_completed_items = 0
    if verification_exists:
        payload = _load_json(verification_path)
        ci_green = str(payload.get("ci_status", "")).strip().lower() == "green"
        try:
            verified_completed_items = int(payload.get("verified_completed_items", 0))
        except Exception:
            verified_completed_items = 0

    if done_marker_present and pending_in_scope > 0:
        findings.append("historical_done_marker_ignored_pending_a_ab")
    if done_marker_present and not verification_exists:
        findings.append("missing_done_marker_verification_evidence")
    if done_marker_present and verification_exists and not ci_green:
        findings.append("done_marker_verification_not_green")
    if done_marker_present and verification_exists and verified_completed_items < completed_in_scope:
        findings.append("done_marker_verification_incomplete_completed_items")

    validator_states: dict[str, str] = {}
    if done_marker_present:
        sec = evidence_root() / "security"
        for report_name in REQUIRED_VALIDATOR_REPORTS:
            report_path = sec / report_name
            if not report_path.exists():
                findings.append(f"missing_required_validator_report:{report_name}")
                validator_states[report_name] = "MISSING"
                continue
            try:
                payload = _load_json(report_path)
            except Exception:
                findings.append(f"invalid_required_validator_report:{report_name}")
                validator_states[report_name] = "INVALID"
                continue
            status = str(payload.get("status", "")).strip().upper()
            validator_states[report_name] = status or "EMPTY"
            if status != "PASS":
                findings.append(f"required_validator_not_pass:{report_name}:{status or 'EMPTY'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "done_marker_present": done_marker_present,
            "pending_in_scope": pending_in_scope,
            "completed_in_scope": completed_in_scope,
            "verification_evidence_path": str(verification_path),
            "verification_evidence_exists": verification_exists,
            "verification_ci_green": ci_green,
            "verified_completed_items": verified_completed_items,
            "required_validator_reports": dict(validator_states),
        },
        "metadata": {"gate": "hardening_done_marker_gate"},
    }
    out = evidence_root() / "security" / "hardening_done_marker_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_DONE_MARKER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
