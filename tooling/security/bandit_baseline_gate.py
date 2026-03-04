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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "bandit_baseline_policy.json"


def _finding_id(item: dict[str, object]) -> str:
    parts = [
        str(item.get("test_id", "")),
        str(item.get("filename", "")),
        str(item.get("line_number", "")),
    ]
    return ":".join(parts)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid bandit baseline policy")

    max_counts = policy.get("max_severity_counts", {})
    if not isinstance(max_counts, dict):
        max_counts = {}
    allowed = policy.get("allowed_findings", [])
    if not isinstance(allowed, list):
        allowed = []
    allowed_set = {str(x) for x in allowed}
    enforce_allowed = bool(policy.get("enforce_approved_findings_only", True))

    bandit_json = ROOT / "bandit.json"
    findings: list[str] = []
    if not bandit_json.exists():
        findings.append("missing_bandit_json")
        results: list[dict[str, object]] = []
    else:
        payload = json.loads(bandit_json.read_text(encoding="utf-8"))
        raw_results = payload.get("results", []) if isinstance(payload, dict) else []
        results = [item for item in raw_results if isinstance(item, dict)]

    severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for item in results:
        severity = str(item.get("issue_severity", "")).upper()
        if severity in severity_counts:
            severity_counts[severity] += 1
        fid = _finding_id(item)
        if enforce_allowed and fid not in allowed_set:
            findings.append(f"unapproved_finding:{fid}")

    for level in ("LOW", "MEDIUM", "HIGH"):
        max_allowed = int(max_counts.get(level, 0))
        observed = severity_counts[level]
        if observed > max_allowed:
            findings.append(f"severity_budget_exceeded:{level}:{observed}:{max_allowed}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "severity_counts": severity_counts,
            "allowed_findings": len(allowed_set),
            "enforce_approved_findings_only": enforce_allowed,
        },
        "metadata": {"gate": "bandit_baseline_gate"},
    }
    out = evidence_root() / "security" / "bandit_baseline_gate.json"
    write_json_report(out, report)
    print(f"BANDIT_BASELINE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
