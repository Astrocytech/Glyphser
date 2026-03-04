#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

JOB_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*$")
CRITICAL_STATUS_CHECKS = {"security-matrix", "branch-protection-policy"}
CRITICAL_RELEASE_CHECKS = {"verify-signatures"}


def _extract_jobs(path: Path) -> set[str]:
    jobs: set[str] = set()
    in_jobs = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip() == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if raw and not raw.startswith(" "):
            break
        if not raw.startswith("  "):
            continue
        if raw.startswith("    "):
            continue
        match = JOB_RE.match(raw.strip())
        if match:
            jobs.add(match.group(1))
    return jobs


def main() -> int:
    policy_path = ROOT / ".github" / "branch-protection.required.json"
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    release_path = ROOT / ".github" / "workflows" / "release.yml"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid branch protection policy format")

    required_checks = policy.get("required_status_checks", [])
    required_release = policy.get("required_release_checks", [])
    required_workflow_jobs = policy.get("required_workflow_jobs", {})
    if not isinstance(required_checks, list) or not all(isinstance(x, str) for x in required_checks):
        raise ValueError("required_status_checks must be list[str]")
    if not isinstance(required_release, list) or not all(isinstance(x, str) for x in required_release):
        raise ValueError("required_release_checks must be list[str]")
    if not isinstance(required_workflow_jobs, dict):
        raise ValueError("required_workflow_jobs must be dict[str, list[str]]")

    ci_jobs = _extract_jobs(ci_path)
    release_jobs = _extract_jobs(release_path)
    missing_ci = sorted([job for job in required_checks if job not in ci_jobs])
    missing_release = sorted([job for job in required_release if job not in release_jobs])
    missing_policy_status_checks = sorted(check for check in CRITICAL_STATUS_CHECKS if check not in required_checks)
    missing_policy_release_checks = sorted(check for check in CRITICAL_RELEASE_CHECKS if check not in required_release)
    missing_workflow_jobs: dict[str, list[str]] = {}
    for filename, jobs in required_workflow_jobs.items():
        if not isinstance(filename, str) or not isinstance(jobs, list) or not all(isinstance(x, str) for x in jobs):
            raise ValueError("required_workflow_jobs entries must be filename -> list[str]")
        wf_path = ROOT / ".github" / "workflows" / filename
        if not wf_path.exists():
            missing_workflow_jobs[filename] = jobs
            continue
        wf_jobs = _extract_jobs(wf_path)
        missing = sorted([job for job in jobs if job not in wf_jobs])
        if missing:
            missing_workflow_jobs[filename] = missing

    status = (
        "PASS"
        if not missing_ci
        and not missing_release
        and not missing_workflow_jobs
        and not missing_policy_status_checks
        and not missing_policy_release_checks
        else "FAIL"
    )
    findings = (
        [f"missing_ci_job:{job}" for job in missing_ci]
        + [f"missing_release_job:{job}" for job in missing_release]
        + [f"missing_policy_status_check:{check}" for check in missing_policy_status_checks]
        + [f"missing_policy_release_check:{check}" for check in missing_policy_release_checks]
    )
    for workflow, jobs in missing_workflow_jobs.items():
        for job in jobs:
            findings.append(f"missing_workflow_job:{workflow}:{job}")
    payload: dict[str, Any] = {
        "status": status,
        "findings": findings,
        "summary": {
            "missing_ci_jobs": len(missing_ci),
            "missing_release_jobs": len(missing_release),
            "missing_workflow_jobs": sum(len(v) for v in missing_workflow_jobs.values()),
        },
        "metadata": {"gate": "branch_protection_policy_gate"},
        "policy_path": str(policy_path.relative_to(ROOT)).replace("\\", "/"),
        "missing_ci_jobs": missing_ci,
        "missing_release_jobs": missing_release,
        "missing_policy_status_checks": missing_policy_status_checks,
        "missing_policy_release_checks": missing_policy_release_checks,
        "missing_workflow_jobs": missing_workflow_jobs,
    }
    out = evidence_root() / "security" / "branch_protection_policy.json"
    write_json_report(out, payload)
    print(f"BRANCH_PROTECTION_POLICY_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
