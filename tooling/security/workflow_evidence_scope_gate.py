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

WORKFLOWS = ROOT / ".github" / "workflows"
EVIDENCE_ROOT_ENV_NAME = "GLYPHSER_EVIDENCE_ROOT"
GUARD_CMD = "tooling/security/evidence_run_dir_guard.py"
RUN_SCOPE_PREFIX = "evidence/runs/${{ github.run_id }}/"


def _needs_evidence_scope(text: str) -> bool:
    if "tooling/security" in text:
        return True
    if "path: evidence/" in text or "path: |\n            evidence/" in text:
        return True
    return False


def _report_for(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    needs = _needs_evidence_scope(text)
    findings: list[str] = []
    if needs and EVIDENCE_ROOT_ENV_NAME not in text:
        findings.append("missing_GLYPHSER_EVIDENCE_ROOT")
    if needs and EVIDENCE_ROOT_ENV_NAME in text and RUN_SCOPE_PREFIX not in text:
        findings.append("invalid_GLYPHSER_EVIDENCE_ROOT_scope")
    if needs and GUARD_CMD not in text:
        findings.append("missing_evidence_run_dir_guard")
    return {
        "workflow": str(path.relative_to(ROOT)).replace("\\", "/"),
        "needs_scope": needs,
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    rows = [_report_for(p) for p in sorted(WORKFLOWS.glob("*.yml"))]
    findings = [f"{r['workflow']}:{k}" for r in rows for k in r["findings"]]
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "total_workflows": len(rows),
            "failing_workflows": sum(1 for r in rows if r["status"] != "PASS"),
            "rows": rows,
        },
        "metadata": {"gate": "workflow_evidence_scope_gate"},
    }
    out = evidence_root() / "security" / "workflow_evidence_scope_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_EVIDENCE_SCOPE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
