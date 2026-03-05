#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RULE_PACK = ROOT / "tooling" / "security" / "workflow_yaml_lint_rules.json"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

DEPENDENT_REPORTS = [
    "workflow_risky_patterns_gate.json",
    "workflow_pinning.json",
    "security_workflow_permissions_policy_gate.json",
]


def _load_rules(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    findings: list[str] = []
    if not path.exists():
        return [], ["missing_workflow_yaml_lint_rule_pack"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], ["invalid_workflow_yaml_lint_rule_pack"]
    if not isinstance(payload, dict):
        return [], ["invalid_workflow_yaml_lint_rule_pack"]
    raw = payload.get("rules", [])
    if not isinstance(raw, list):
        return [], ["invalid_workflow_yaml_lint_rules"]
    rules: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            findings.append("invalid_workflow_yaml_lint_rule_entry")
            continue
        rule_id = str(item.get("id", "")).strip()
        pattern = str(item.get("pattern", "")).strip()
        if not rule_id or not pattern:
            findings.append("invalid_workflow_yaml_lint_rule_fields")
            continue
        rules.append({"id": rule_id, "pattern": pattern})
    return rules, findings


def _scan_workflows(rules: list[dict[str, str]]) -> list[str]:
    findings: list[str] = []
    if not WORKFLOWS_DIR.exists():
        return ["missing_workflows_directory"]
    for wf in sorted(WORKFLOWS_DIR.glob("*.yml")):
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        text = wf.read_text(encoding="utf-8")
        for rule in rules:
            rule_id = rule["id"]
            pattern = rule["pattern"]
            for lineno, line in enumerate(text.splitlines(), start=1):
                if re.search(pattern, line):
                    findings.append(f"lint_rule_violation:{rule_id}:{rel}:{lineno}")
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked = 0

    for name in DEPENDENT_REPORTS:
        checked += 1
        path = sec / name
        if not path.exists():
            findings.append(f"missing_dependency_report:{name}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_dependency_report_json:{name}")
            continue
        status = str(payload.get("status", "")).upper()
        if status != "PASS":
            findings.append(f"dependency_report_not_pass:{name}:{status or 'UNKNOWN'}")

    rules, rule_pack_findings = _load_rules(RULE_PACK)
    findings.extend(rule_pack_findings)
    if not rule_pack_findings:
        findings.extend(_scan_workflows(rules))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_dependency_reports": checked,
            "rule_pack_path": str(RULE_PACK.relative_to(ROOT)).replace("\\", "/"),
            "rule_count": len(rules),
        },
        "metadata": {"gate": "workflow_linter_gate"},
    }
    out = sec / "workflow_linter_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_LINTER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
