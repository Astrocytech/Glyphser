#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

CHECKLIST = ROOT / "governance" / "security" / "ENVELOPE_SIGNATURE_MULTI_SIGNER_CHECKLIST.md"
REQUIRED_SNIPPETS = [
    "canonical envelope structure",
    "signer identity requirements",
    "deterministic signer ordering",
    "threshold policy (`M-of-N`)",
    "signer role separation constraints",
    "key rotation behavior",
    "revocation behavior",
    "partial signature failure semantics",
    "replay protection requirements",
    "verification evidence output format",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    text = CHECKLIST.read_text(encoding="utf-8") if CHECKLIST.exists() else ""
    if not text:
        findings.append("missing_or_empty_multi_signer_checklist")
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            findings.append(f"missing_checklist_requirement:{snippet}")
    checked_items = [line for line in text.splitlines() if line.strip().startswith("- [x]")]
    if len(checked_items) < len(REQUIRED_SNIPPETS):
        findings.append("checklist_not_fully_defined")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"required_items": len(REQUIRED_SNIPPETS), "checked_items": len(checked_items)},
        "metadata": {"gate": "envelope_signature_design_checklist_gate"},
    }
    out = evidence_root() / "security" / "envelope_signature_design_checklist_gate.json"
    write_json_report(out, report)
    print(f"ENVELOPE_SIGNATURE_DESIGN_CHECKLIST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
