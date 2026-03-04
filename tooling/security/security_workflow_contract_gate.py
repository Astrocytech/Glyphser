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

REQUIRED_SNIPPETS = [
    "security-matrix:",
    "security-events: write",
    "semgrep==1.95.0",
    "setuptools==75.8.0",
    "if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false",
    "python tooling/security/evidence_run_dir_guard.py --run-id",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    findings: list[str] = []
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in ci:
            findings.append(f"missing_workflow_contract_snippet:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"required_snippets": len(REQUIRED_SNIPPETS), "checked_workflow": ".github/workflows/ci.yml"},
        "metadata": {"gate": "security_workflow_contract_gate"},
    }
    out = evidence_root() / "security" / "security_workflow_contract_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_WORKFLOW_CONTRACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
