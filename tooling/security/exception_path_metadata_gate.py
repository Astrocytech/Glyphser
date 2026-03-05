#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXCEPTIONS_FILE = ROOT / "governance" / "security" / "temporary_exceptions.json"
WAIVERS_FILE = ROOT / "evidence" / "repro" / "waivers.json"
JUSTIFICATION_FIELDS = ("justification", "reason")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _has_value(entry: dict[str, Any], key: str) -> bool:
    return bool(str(entry.get(key, "")).strip())


def _has_justification(entry: dict[str, Any]) -> bool:
    return any(_has_value(entry, key) for key in JUSTIFICATION_FIELDS)


def _check_entries(entries: Any, kind: str, findings: list[str]) -> int:
    if not isinstance(entries, list):
        findings.append(f"invalid_{kind}_list")
        return 0

    valid = 0
    for idx, item in enumerate(entries):
        if not isinstance(item, dict):
            findings.append(f"invalid_{kind}_entry_type:{idx}")
            continue
        if not _has_value(item, "owner"):
            findings.append(f"missing_owner:{kind}:{idx}")
        if not _has_value(item, "expires_at_utc"):
            findings.append(f"missing_expiry:{kind}:{idx}")
        if not _has_justification(item):
            findings.append(f"missing_justification:{kind}:{idx}")
        valid += 1
    return valid


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not EXCEPTIONS_FILE.exists():
        findings.append("missing_temporary_exceptions_file")
        exceptions_payload = {}
    else:
        try:
            exceptions_payload = _load_json(EXCEPTIONS_FILE)
        except Exception:
            findings.append("invalid_temporary_exceptions_file")
            exceptions_payload = {}

    if not WAIVERS_FILE.exists():
        waivers_payload = {}
    else:
        try:
            waivers_payload = _load_json(WAIVERS_FILE)
        except Exception:
            findings.append("invalid_waivers_file")
            waivers_payload = {}

    checked_exceptions = _check_entries(exceptions_payload.get("exceptions", []), "exception", findings)
    checked_waivers = _check_entries(waivers_payload.get("waivers", []), "waiver", findings)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_exception_entries": checked_exceptions,
            "checked_waiver_entries": checked_waivers,
            "temporary_exceptions_path": str(EXCEPTIONS_FILE.relative_to(ROOT)).replace("\\", "/"),
            "waivers_path": str(WAIVERS_FILE.relative_to(ROOT)).replace("\\", "/"),
            "justification_fields": list(JUSTIFICATION_FIELDS),
        },
        "metadata": {"gate": "exception_path_metadata_gate"},
    }
    out = evidence_root() / "security" / "exception_path_metadata_gate.json"
    write_json_report(out, report)
    print(f"EXCEPTION_PATH_METADATA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
