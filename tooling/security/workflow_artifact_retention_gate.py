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

POLICY = ROOT / "governance" / "security" / "workflow_artifact_retention_policy.json"


def _load_policy() -> tuple[dict[str, str], dict[str, int]]:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}, {}

    classes_raw = payload.get("workflow_classes", {})
    days_raw = payload.get("retention_days_by_class", {})

    classes: dict[str, str] = {}
    days: dict[str, int] = {}

    if isinstance(classes_raw, dict):
        for workflow, cls in classes_raw.items():
            workflow_name = str(workflow).strip()
            class_name = str(cls).strip()
            if workflow_name and class_name:
                classes[workflow_name] = class_name
    if isinstance(days_raw, dict):
        for cls, retention in days_raw.items():
            class_name = str(cls).strip()
            if not class_name:
                continue
            try:
                days[class_name] = int(retention)
            except (TypeError, ValueError):
                continue
    return classes, days


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY.exists():
        findings.append("missing_retention_policy")
    workflow_classes, retention_days_by_class = _load_policy() if POLICY.exists() else ({}, {})
    if not workflow_classes:
        findings.append("invalid_workflow_retention_policy:missing_workflow_classes")
    if not retention_days_by_class:
        findings.append("invalid_workflow_retention_policy:missing_retention_days_by_class")
    checked = 0
    workflows_dir = ROOT / ".github" / "workflows"
    for name, cls in sorted(workflow_classes.items()):
        path = workflows_dir / name
        if not path.exists():
            findings.append(f"missing_workflow:{name}")
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        expected_days = retention_days_by_class.get(cls)
        if expected_days is None:
            findings.append(f"undefined_retention_class:{name}:{cls}")
            continue
        required = f"retention-days: {expected_days}"
        if "actions/upload-artifact@" in text and required not in text:
            findings.append(f"missing_retention_policy:{name}:{required}:class={cls}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_workflows": checked,
            "required_workflows": len(workflow_classes),
            "retention_classes": sorted(retention_days_by_class),
        },
        "metadata": {"gate": "workflow_artifact_retention_gate", "policy_path": str(POLICY.relative_to(ROOT))},
    }
    out = evidence_root() / "security" / "workflow_artifact_retention_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_ARTIFACT_RETENTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
