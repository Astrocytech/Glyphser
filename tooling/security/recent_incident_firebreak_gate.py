#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "recent_incident_firebreak_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_changed_files(raw: str) -> list[str]:
    out: list[str] = []
    for token in raw.replace("\n", ",").split(","):
        value = token.strip().replace("\\", "/")
        if value:
            out.append(value)
    return sorted(set(out))


def _load_status(report_name: str) -> str:
    path = evidence_root() / "security" / report_name
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def _path_matches(changed: str, prefix: str) -> bool:
    normalized = prefix.strip().strip("/")
    if not normalized:
        return False
    return changed == normalized or changed.startswith(f"{normalized}/")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Block merges touching paths from recent incidents unless additional checks pass."
    )
    parser.add_argument(
        "--changed-files",
        default="",
        help="Comma/newline-separated changed files. Falls back to GLYPHSER_CHANGED_FILES env var.",
    )
    args = parser.parse_args([] if argv is None else argv)

    findings: list[str] = []
    checks: list[dict[str, Any]] = []

    if not POLICY.exists():
        findings.append("missing_recent_incident_firebreak_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    incidents = policy.get("active_incidents", [])
    if not isinstance(incidents, list):
        incidents = []
        findings.append("invalid_firebreak_policy_active_incidents")

    changed_raw = args.changed_files.strip() or os.environ.get("GLYPHSER_CHANGED_FILES", "")
    changed_files = _parse_changed_files(changed_raw)

    triggered = 0
    for item in incidents:
        if not isinstance(item, dict):
            findings.append("invalid_firebreak_incident_entry")
            continue
        incident_id = str(item.get("incident_id", "")).strip() or "unknown_incident"
        affected_paths = [str(p).strip() for p in item.get("affected_paths", []) if str(p).strip()]
        required_reports = [str(p).strip() for p in item.get("required_reports", []) if str(p).strip()]
        if not affected_paths or not required_reports:
            findings.append(f"invalid_firebreak_incident_policy:{incident_id}")
            continue

        touched = sorted(
            {path for path in changed_files for prefix in affected_paths if _path_matches(path, prefix)}
        )
        if not touched:
            continue

        triggered += 1
        report_checks: list[dict[str, str]] = []
        for report_name in required_reports:
            status = _load_status(report_name)
            report_checks.append({"report": report_name, "status": status})
            if status != "PASS":
                findings.append(f"firebreak_required_check_not_pass:{incident_id}:{report_name}:{status}")

        checks.append(
            {
                "incident_id": incident_id,
                "touched_paths": touched,
                "required_report_checks": report_checks,
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "changed_files_count": len(changed_files),
            "active_incidents": len(incidents),
            "triggered_incidents": triggered,
        },
        "metadata": {"gate": "recent_incident_firebreak_gate"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "recent_incident_firebreak_gate.json"
    write_json_report(out, report)
    print(f"RECENT_INCIDENT_FIREBREAK_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
