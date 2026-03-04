#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

CHECKLIST = ROOT / "governance" / "security" / "SECURITY_GATE_ONBOARDING_CHECKLIST.md"
REQUIRED_PHRASES = [
    "status",
    "findings",
    "summary",
    "metadata",
    "tests/security",
    "security_super_gate.py",
    "security_super_gate_manifest.json",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not CHECKLIST.exists():
        findings.append("missing_checklist:governance/security/SECURITY_GATE_ONBOARDING_CHECKLIST.md")
        text = ""
    else:
        text = CHECKLIST.read_text(encoding="utf-8")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            findings.append(f"missing_checklist_phrase:{phrase}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checklist": str(CHECKLIST.relative_to(ROOT)).replace("\\", "/"),
            "required_phrases": REQUIRED_PHRASES,
        },
        "metadata": {"gate": "security_gate_onboarding_checklist_gate"},
    }
    out = evidence_root() / "security" / "security_gate_onboarding_checklist_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_GATE_ONBOARDING_CHECKLIST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
