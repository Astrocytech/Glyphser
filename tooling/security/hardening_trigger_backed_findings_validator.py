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

WEEKLY_TRIAGE = ROOT / "evidence" / "security" / "weekly_hardening_triage.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    unresolved_count = 0

    if not WEEKLY_TRIAGE.exists():
        findings.append("missing_weekly_hardening_triage_report")
    else:
        triage = _load_json(WEEKLY_TRIAGE)
        candidates = triage.get("candidates", []) if isinstance(triage.get("candidates", []), list) else []
        unresolved_count = len([item for item in candidates if isinstance(item, dict)])
        if unresolved_count > 0:
            findings.append(f"unresolved_trigger_backed_findings:{unresolved_count}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "unresolved_trigger_backed_findings": unresolved_count,
        },
        "metadata": {"validator": "hardening_trigger_backed_findings_validator"},
    }
    out = evidence_root() / "security" / "hardening_trigger_backed_findings_validator.json"
    write_json_report(out, report)
    print(f"HARDENING_TRIGGER_BACKED_FINDINGS_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
