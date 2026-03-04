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
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    review = json.loads((ROOT / "governance" / "security" / "review_policy.json").read_text(encoding="utf-8"))
    branch = json.loads((ROOT / ".github" / "branch-protection.required.json").read_text(encoding="utf-8"))
    findings: list[str] = []

    if int(review.get("minimum_required_approvals", 0)) < int(policy.get("required_branch_approvals", 2)):
        findings.append("review_policy_approvals_below_threshold")
    if int(branch.get("minimum_required_approvals", 0)) < int(policy.get("required_branch_approvals", 2)):
        findings.append("branch_policy_approvals_below_threshold")

    groups = review.get("approval_groups", {}) if isinstance(review, dict) else {}
    if not isinstance(groups, dict) or "policy_changes" not in groups or "workflow_unlock" not in groups:
        findings.append("missing_split_duty_groups")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_branch_approvals": int(policy.get("required_branch_approvals", 2)),
            "review_policy_approvals": int(review.get("minimum_required_approvals", 0)),
            "branch_policy_approvals": int(branch.get("minimum_required_approvals", 0)),
        },
        "metadata": {"gate": "split_duty_gate"},
    }
    out = evidence_root() / "security" / "split_duty_gate.json"
    write_json_report(out, report)
    print(f"SPLIT_DUTY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
