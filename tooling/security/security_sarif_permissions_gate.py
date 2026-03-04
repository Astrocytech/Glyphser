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

SARIF_ACTION = "github/codeql-action/upload-sarif@"
FORK_GUARD = "if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false"
SEC_EVENTS_PERMISSION = "security-events: write"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    findings: list[str] = []
    checked = 0
    with_sarif = 0

    for wf in workflows:
        text = wf.read_text(encoding="utf-8")
        checked += 1
        if SARIF_ACTION not in text:
            continue
        with_sarif += 1
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        if FORK_GUARD not in text:
            findings.append(f"missing_fork_guard:{rel}")
        if SEC_EVENTS_PERMISSION not in text:
            findings.append(f"missing_security_events_permission:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "sarif_workflows": with_sarif},
        "metadata": {"gate": "security_sarif_permissions_gate"},
    }
    out = evidence_root() / "security" / "security_sarif_permissions_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SARIF_PERMISSIONS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
