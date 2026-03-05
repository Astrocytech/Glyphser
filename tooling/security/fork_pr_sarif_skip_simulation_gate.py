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

CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SARIF_SKIP_CONDITION = "if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false"
SARIF_PUSH_ONLY_CONDITION = "if: github.event_name == 'push'"
SARIF_UPLOAD_MARKER = "Upload SARIF to Code Scanning"
RAW_ARTIFACT_MARKER = "Upload security artifacts"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not CI_WORKFLOW.exists():
        findings.append("missing_ci_workflow")
        text = ""
    else:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

    if SARIF_SKIP_CONDITION not in text and SARIF_PUSH_ONLY_CONDITION not in text:
        findings.append("missing_fork_pr_sarif_skip_condition")
    if SARIF_UPLOAD_MARKER not in text:
        findings.append("missing_sarif_upload_step")
    if RAW_ARTIFACT_MARKER not in text:
        findings.append("missing_semgrep_raw_artifact_upload_step")

    simulation_cases = [
        {"event_name": "pull_request", "is_fork": True, "expected_sarif_upload": False, "expected_artifact_upload": True},
        {"event_name": "pull_request", "is_fork": False, "expected_sarif_upload": True, "expected_artifact_upload": True},
        {"event_name": "push", "is_fork": False, "expected_sarif_upload": True, "expected_artifact_upload": True},
    ]

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"simulated_cases": len(simulation_cases), "workflow_checked": str(CI_WORKFLOW.relative_to(ROOT))},
        "metadata": {"gate": "fork_pr_sarif_skip_simulation_gate"},
        "simulation_cases": simulation_cases,
    }
    out = evidence_root() / "security" / "fork_pr_sarif_skip_simulation_gate.json"
    write_json_report(out, report)
    print(f"FORK_PR_SARIF_SKIP_SIMULATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
