#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DOCS = [
    ROOT / "governance" / "security" / "SECURITY_ARCHITECTURE.md",
    ROOT / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md",
    ROOT / "governance" / "security" / "INCIDENT_RUNBOOKS.md",
    ROOT / "governance" / "security" / "GATE_RUNBOOK_INDEX.md",
    ROOT / "governance" / "security" / "KNOWN_CI_FAILURE_MODES.md",
    ROOT / "governance" / "security" / "EMERGENCY_BYPASS_PROCESS.md",
    ROOT / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md",
    ROOT / "governance" / "security" / "OPERATOR_SIGNED_ARTIFACTS_QUICKSTART.md",
]

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_links: list[str] = []
    for doc in DOCS:
        if not doc.exists():
            findings.append(f"missing_doc:{doc}")
            continue
        text = doc.read_text(encoding="utf-8")
        for link in LINK_RE.findall(text):
            if "://" in link:
                continue
            target = (doc.parent / link).resolve()
            checked_links.append(link)
            if not target.exists():
                findings.append(f"broken_link:{doc.name}:{link}")

    must_exist = [
        ROOT / "tooling" / "security" / "security_super_gate.py",
        ROOT / "governance" / "security" / "review_policy.json",
        ROOT / ".github" / "workflows" / "security-maintenance.yml",
    ]
    for path in must_exist:
        if not path.exists():
            findings.append(f"missing_reference_target:{path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "docs_checked": [str(d.relative_to(ROOT)).replace("\\", "/") for d in DOCS],
            "relative_links_checked": len(checked_links),
        },
        "metadata": {"gate": "security_docs_traceability_gate"},
    }
    out = evidence_root() / "security" / "security_docs_traceability_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_DOCS_TRACEABILITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
