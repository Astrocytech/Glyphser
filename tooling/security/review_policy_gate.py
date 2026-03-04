#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked


def _run(cmd: list[str]) -> str:
    proc = run_checked(cmd, cwd=ROOT)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "review_policy.json").read_text(encoding="utf-8"))
    findings: list[str] = []

    codeowners = ROOT / ".github" / "CODEOWNERS"
    if not codeowners.exists():
        findings.append("missing_codeowners")
    else:
        text = codeowners.read_text(encoding="utf-8")
        for path in policy.get("required_codeowners_paths", []):
            if isinstance(path, str) and path not in text:
                findings.append(f"missing_codeowner_rule:{path}")

    bp = json.loads((ROOT / ".github" / "branch-protection.required.json").read_text(encoding="utf-8"))
    min_approvals = int(policy.get("minimum_required_approvals", 2))
    if int(bp.get("minimum_required_approvals", 0)) < min_approvals:
        findings.append("branch_protection_approvals_too_low")

    changed = _run(["git", "diff", "--name-only", "HEAD~1", "HEAD"]).splitlines()
    baseline_paths = [p for p in policy.get("security_baseline_paths", []) if isinstance(p, str)]
    if any(p in changed for p in baseline_paths):
        ticket = os.environ.get("GLYPHSER_CHANGE_TICKET", "")
        patterns = [p for p in policy.get("required_change_ticket_patterns", []) if isinstance(p, str)]
        if not any(tok in ticket for tok in patterns):
            findings.append("baseline_change_missing_ticket_or_adr")

    security_paths = [p for p in changed if p.startswith("tooling/security/") or p.startswith("governance/security/")]
    changelog = str(policy.get("required_changelog_file", "")).strip()
    if security_paths and changelog and changelog not in changed:
        findings.append("missing_security_changelog_entry")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"changed_files": len(changed), "security_changed_files": len(security_paths)},
        "metadata": {"gate": "review_policy_gate", "min_approvals": min_approvals},
    }
    out = evidence_root() / "security" / "review_policy_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REVIEW_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
