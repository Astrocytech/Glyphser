#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOW_RETENTION = {
    "ci.yml": "retention-days: 14",
    "security-maintenance.yml": "retention-days: 30",
    "security-super-extended.yml": "retention-days: 30",
    "release.yml": "retention-days: 180",
}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    workflows_dir = ROOT / ".github" / "workflows"
    for name, required in WORKFLOW_RETENTION.items():
        path = workflows_dir / name
        if not path.exists():
            findings.append(f"missing_workflow:{name}")
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        if "actions/upload-artifact@" in text and required not in text:
            findings.append(f"missing_retention_policy:{name}:{required}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "required_workflows": len(WORKFLOW_RETENTION)},
        "metadata": {"gate": "workflow_artifact_retention_gate"},
    }
    out = evidence_root() / "security" / "workflow_artifact_retention_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_ARTIFACT_RETENTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
