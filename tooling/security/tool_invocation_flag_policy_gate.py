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

POLICY = ROOT / "governance" / "security" / "tool_invocation_flag_policy.json"
WORKFLOWS = ROOT / ".github" / "workflows"


def _load_policy() -> list[dict]:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        return []
    out: list[dict] = []
    for item in tools:
        if isinstance(item, dict):
            out.append(item)
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY.exists():
        findings.append("missing_tool_invocation_flag_policy")
        tool_rules: list[dict] = []
    else:
        tool_rules = _load_policy()
        if not tool_rules:
            findings.append("invalid_or_empty_tool_invocation_flag_policy")

    workflow_lines: list[tuple[str, int, str]] = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), start=1):
            workflow_lines.append((rel, idx, line))

    for rule in tool_rules:
        rule_id = str(rule.get("id", "")).strip() or "unknown"
        match = str(rule.get("match", "")).strip()
        required_flags = [str(flag).strip() for flag in rule.get("required_flags", []) if str(flag).strip()]
        forbidden_flags = [str(flag).strip() for flag in rule.get("forbidden_flags", []) if str(flag).strip()]
        required_any_flags_raw = rule.get("required_any_flags", [])
        required_any_flags: list[list[str]] = []
        if isinstance(required_any_flags_raw, list):
            for group in required_any_flags_raw:
                if not isinstance(group, list):
                    continue
                flags = [str(flag).strip() for flag in group if str(flag).strip()]
                if flags:
                    required_any_flags.append(flags)

        if not match:
            findings.append(f"invalid_rule_missing_match:{rule_id}")
            continue

        matched = [(path, line_no, line) for path, line_no, line in workflow_lines if match in line]
        if not matched:
            findings.append(f"missing_invocation:{rule_id}:{match}")
            continue

        for path, line_no, line in matched:
            for flag in required_flags:
                if flag not in line:
                    findings.append(f"missing_required_flag:{rule_id}:{path}:{line_no}:{flag}")
            for flag_group in required_any_flags:
                if not any(flag in line for flag in flag_group):
                    findings.append(
                        f"missing_required_flag_group:{rule_id}:{path}:{line_no}:{'|'.join(flag_group)}"
                    )
            for flag in forbidden_flags:
                if flag in line:
                    findings.append(f"forbidden_flag:{rule_id}:{path}:{line_no}:{flag}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflow_files_scanned": len(list(WORKFLOWS.glob("*.yml"))),
            "policy_rules": len(tool_rules),
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "tool_invocation_flag_policy_gate"},
    }
    out = evidence_root() / "security" / "tool_invocation_flag_policy_gate.json"
    write_json_report(out, report)
    print(f"TOOL_INVOCATION_FLAG_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
