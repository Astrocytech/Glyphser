#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

WORKFLOWS = ROOT / ".github" / "workflows"
SECRET_REF = "${{ secrets."
FORK_GUARDS = (
    "github.event.pull_request.head.repo.fork == false",
    "!github.event.pull_request.head.repo.fork",
    "github.event_name != 'pull_request'",
    "github.event_name != \"pull_request\"",
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    guarded = 0

    for path in sorted(WORKFLOWS.glob("*.yml")):
        name = path.name
        if not (name.startswith("security-") or name == "release.yml"):
            continue
        text = path.read_text(encoding="utf-8")
        if "pull_request:" not in text:
            continue
        if SECRET_REF not in text:
            continue
        checked += 1
        if any(guard in text for guard in FORK_GUARDS):
            guarded += 1
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        findings.append(f"unguarded_secret_usage_in_pull_request_workflow:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "pull_request_workflows_with_secrets": checked,
            "guarded_workflows": guarded,
            "verification_artifact": "untrusted_pr_secret_isolation_gate.json",
        },
        "metadata": {"gate": "untrusted_pr_secret_isolation_gate"},
    }
    out = evidence_root() / "security" / "untrusted_pr_secret_isolation_gate.json"
    write_json_report(out, report)
    print(f"UNTRUSTED_PR_SECRET_ISOLATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
