#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root

JOB_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*$")


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
    if not isinstance(required_checks, list) or not all(isinstance(x, str) for x in required_checks):
        raise ValueError("required_status_checks must be list[str]")
    if not isinstance(required_release, list) or not all(isinstance(x, str) for x in required_release):
        raise ValueError("required_release_checks must be list[str]")

    ci_jobs = _extract_jobs(ci_path)
    release_jobs = _extract_jobs(release_path)
    missing_ci = sorted([job for job in required_checks if job not in ci_jobs])
    missing_release = sorted([job for job in required_release if job not in release_jobs])

    status = "PASS" if not missing_ci and not missing_release else "FAIL"
    payload: dict[str, Any] = {
        "status": status,
        "policy_path": str(policy_path.relative_to(ROOT)).replace("\\", "/"),
        "missing_ci_jobs": missing_ci,
        "missing_release_jobs": missing_release,
    }
    out = evidence_root() / "security" / "branch_protection_policy.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BRANCH_PROTECTION_POLICY_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
