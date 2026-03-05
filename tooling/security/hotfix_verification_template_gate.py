#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TEMPLATE = ROOT / "governance" / "security" / "hotfix_verification_template.md"
REQUIRED_MARKERS = (
    "## Before Fix (Failing Test Proof)",
    "- Test command:",
    "- Failure output artifact path:",
    "## After Fix (Passing Test Proof)",
    "- Test command:",
    "- Passing output artifact path:",
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not TEMPLATE.exists():
        findings.append("missing_hotfix_verification_template")
        text = ""
    else:
        text = TEMPLATE.read_text(encoding="utf-8")

    missing_markers: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            missing_markers.append(marker)
            findings.append(f"missing_hotfix_template_marker:{marker}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "template_path": str(TEMPLATE),
            "required_markers": len(REQUIRED_MARKERS),
            "missing_markers": len(missing_markers),
        },
        "metadata": {"gate": "hotfix_verification_template_gate"},
    }
    out = evidence_root() / "security" / "hotfix_verification_template_gate.json"
    write_json_report(out, report)
    print(f"HOTFIX_VERIFICATION_TEMPLATE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
