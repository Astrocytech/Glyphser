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

POLICY = ROOT / "governance" / "security" / "scheduled_workflow_backpressure_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_scheduled_workflow_backpressure_policy")
        workflows: list[str] = []
        required = {}
    else:
        try:
            payload = _load_json(POLICY)
        except Exception:
            payload = {}
            findings.append("invalid_scheduled_workflow_backpressure_policy")
        raw = payload.get("scheduled_hardening_workflows", []) if isinstance(payload, dict) else []
        workflows = [str(item).strip() for item in raw if isinstance(item, str) and str(item).strip()]
        required = payload.get("required_concurrency", {}) if isinstance(payload, dict) else {}

    group_contains = str(required.get("group_must_contain", "${{ github.workflow }}")).strip() if isinstance(required, dict) else "${{ github.workflow }}"
    cancel_in_progress = bool(required.get("cancel_in_progress", False)) if isinstance(required, dict) else False

    checked = 0
    for rel in workflows:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        checked += 1
        if "schedule:" not in text:
            findings.append(f"workflow_missing_schedule_trigger:{rel}")
        if "concurrency:" not in text:
            findings.append(f"workflow_missing_concurrency:{rel}")
            continue
        if group_contains and group_contains not in text:
            findings.append(f"workflow_concurrency_group_missing_marker:{rel}:{group_contains}")
        required_text = f"cancel-in-progress: {'true' if cancel_in_progress else 'false'}"
        if required_text not in text:
            findings.append(f"workflow_concurrency_cancel_setting_mismatch:{rel}:{required_text}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "configured_workflows": len(workflows),
            "checked_workflows": checked,
            "required_cancel_in_progress": cancel_in_progress,
        },
        "metadata": {"gate": "scheduled_workflow_backpressure_gate"},
    }
    out = evidence_root() / "security" / "scheduled_workflow_backpressure_gate.json"
    write_json_report(out, report)
    print(f"SCHEDULED_WORKFLOW_BACKPRESSURE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
