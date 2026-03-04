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

CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"
REQUIRED_SNIPPETS = (
    "security-matrix:",
    "on:",
    "push:",
    "pull_request:",
    "name: Security targeted regression suite",
    "run: pytest -q tests/security",
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not CI_PATH.exists():
        findings.append("missing_workflow:.github/workflows/ci.yml")
        checked = 0
    else:
        checked = 1
        text = CI_PATH.read_text(encoding="utf-8")
        for snippet in REQUIRED_SNIPPETS:
            if snippet not in text:
                findings.append(f"missing_required_snippet:.github/workflows/ci.yml:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "required_snippets": len(REQUIRED_SNIPPETS)},
        "metadata": {"gate": "security_critical_test_wiring_gate"},
    }
    out = evidence_root() / "security" / "security_critical_test_wiring_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_CRITICAL_TEST_WIRING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
