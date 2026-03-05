#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY_PATH = ROOT / "governance" / "security" / "workflow_retrofit_policy.json"
MASKED_EXIT_RE = re.compile(r"\|\|\s*(?:true|:)|;\s*true\b|\bset\s+\+e\b")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _step_blocks(text: str) -> list[tuple[int, list[str]]]:
    blocks: list[tuple[int, list[str]]] = []
    current: list[str] = []
    start_line = 1
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("- name:"):
            if current:
                blocks.append((start_line, current))
            current = [line]
            start_line = line_no
            continue
        if current:
            current.append(line)
    if current:
        blocks.append((start_line, current))
    return blocks


def _has_continue_on_error_true(block: list[str]) -> bool:
    for line in block:
        stripped = line.strip().lower()
        if stripped.startswith("continue-on-error:") and "true" in stripped:
            return True
    return False


def _has_if_condition(block: list[str]) -> bool:
    return any(line.strip().startswith("if:") for line in block)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY_PATH.exists():
        findings.append("missing_workflow_retrofit_policy")
        policy = {}
    else:
        try:
            policy = _load_json(POLICY_PATH)
        except Exception:
            findings.append("invalid_workflow_retrofit_policy")
            policy = {}

    mandatory_workflows = policy.get("mandatory_workflows", []) if isinstance(policy, dict) else []
    required_controls = policy.get("required_controls", []) if isinstance(policy, dict) else []

    workflows = [str(item).strip() for item in mandatory_workflows if isinstance(item, str) and str(item).strip()]
    controls = [str(item).strip() for item in required_controls if isinstance(item, str) and str(item).strip()]

    checked_workflows = 0
    fail_closed_hits = 0

    for rel in workflows:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        checked_workflows += 1
        blocks = _step_blocks(path.read_text(encoding="utf-8"))
        workflow_has_fail_closed_control = False

        for start_line, block in blocks:
            block_text = "\n".join(block)
            has_continue_on_error = _has_continue_on_error_true(block)
            has_if = _has_if_condition(block)
            for control in controls:
                if control not in block_text:
                    continue
                if has_continue_on_error:
                    findings.append(f"fail_open_control_continue_on_error:{rel}:{start_line}:{control}")
                    continue
                if has_if:
                    findings.append(f"conditional_control_in_strict_lane:{rel}:{start_line}:{control}")
                    continue
                masked = False
                for idx, line in enumerate(block, start=start_line):
                    if control in line and MASKED_EXIT_RE.search(line):
                        findings.append(f"masked_control_exit:{rel}:{idx}:{control}")
                        masked = True
                        break
                if masked:
                    continue
                workflow_has_fail_closed_control = True
                fail_closed_hits += 1

        if not workflow_has_fail_closed_control:
            findings.append(f"missing_fail_closed_control:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_checked": checked_workflows,
            "required_controls": len(controls),
            "fail_closed_controls_found": fail_closed_hits,
        },
        "metadata": {"gate": "strict_lane_fail_closed_control_gate"},
    }
    out = evidence_root() / "security" / "strict_lane_fail_closed_control_gate.json"
    write_json_report(out, report)
    print(f"STRICT_LANE_FAIL_CLOSED_CONTROL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
