#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY_PATH = ROOT / "governance" / "security" / "workflow_retrofit_policy.json"
WARNING_LANE_INDICATORS = (
    "python tooling/security/temporary_waiver_gate.py",
    "--allow-dry-run",
    "continue-on-error: true",
)
DEGRADED_MODE_COMMAND = "python tooling/security/degraded_mode_evidence.py"
DEGRADED_MODE_ARTIFACT = "degraded_mode_evidence.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


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

    workflows_raw = policy.get("mandatory_workflows", []) if isinstance(policy, dict) else []
    workflows = [str(item).strip() for item in workflows_raw if isinstance(item, str) and str(item).strip()]

    checked_workflows = 0
    warning_lanes = 0

    for rel in workflows:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        checked_workflows += 1
        text = path.read_text(encoding="utf-8")
        is_warning_lane = any(indicator in text for indicator in WARNING_LANE_INDICATORS)
        if not is_warning_lane:
            continue
        warning_lanes += 1
        if DEGRADED_MODE_COMMAND not in text:
            findings.append(f"warning_lane_missing_degraded_mode_command:{rel}")
        if DEGRADED_MODE_ARTIFACT not in text:
            findings.append(f"warning_lane_missing_degraded_mode_artifact:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_checked": checked_workflows,
            "warning_lanes_detected": warning_lanes,
            "required_command": DEGRADED_MODE_COMMAND,
            "required_artifact": DEGRADED_MODE_ARTIFACT,
        },
        "metadata": {"gate": "warning_lane_degraded_mode_artifact_gate"},
    }
    out = evidence_root() / "security" / "warning_lane_degraded_mode_artifact_gate.json"
    write_json_report(out, report)
    print(f"WARNING_LANE_DEGRADED_MODE_ARTIFACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
