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

SECURITY_TOOLING = ROOT / "tooling" / "security"
WORKFLOW = ROOT / ".github" / "workflows" / "security-maintenance.yml"
CRITICAL_ARTIFACTS_POLICY = ROOT / "governance" / "security" / "security_critical_artifacts.json"
PRODUCED_RE = re.compile(r'evidence_root\(\)\s*/\s*"security"\s*/\s*"(?P<name>[^"]+\.json(?:\.sig)?)"')
UPLOADED_RE = re.compile(r"/security/(?P<name>[A-Za-z0-9_.-]+\.json(?:\.sig)?)")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _produced_names() -> set[str]:
    names: set[str] = set()
    if not SECURITY_TOOLING.exists():
        return names
    for path in sorted(SECURITY_TOOLING.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in PRODUCED_RE.finditer(text):
            names.add(match.group("name"))
    return names


def _uploaded_names() -> set[str]:
    if not WORKFLOW.exists():
        return set()
    names: set[str] = set()
    text = WORKFLOW.read_text(encoding="utf-8")
    for match in UPLOADED_RE.finditer(text):
        names.add(match.group("name"))
    return names


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    produced = _produced_names()
    uploaded = _uploaded_names()

    if not WORKFLOW.exists():
        findings.append("missing_security_maintenance_workflow")

    unmatched: list[str] = []
    for name in sorted(uploaded):
        if name.endswith(".sig"):
            base = name[:-4]
            if base not in produced and name not in produced:
                unmatched.append(name)
            continue
        if name not in produced:
            unmatched.append(name)

    if unmatched:
        findings.append(f"uploaded_artifacts_without_producer:{len(unmatched)}")

    critical_missing: list[str] = []
    if CRITICAL_ARTIFACTS_POLICY.exists():
        policy = _load_json(CRITICAL_ARTIFACTS_POLICY)
        critical = [
            str(item).strip()
            for item in policy.get("critical_artifacts", [])
            if str(item).strip()
        ] if isinstance(policy.get("critical_artifacts", []), list) else []
        for name in critical:
            if name in produced and name not in uploaded:
                critical_missing.append(name)
    if critical_missing:
        findings.append(f"critical_artifacts_missing_upload:{len(critical_missing)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "produced_artifacts": len(produced),
            "uploaded_artifacts": len(uploaded),
            "unmatched_uploads": len(unmatched),
            "critical_missing_uploads": len(critical_missing),
        },
        "metadata": {"validator": "security_workflow_artifact_coverage_validator"},
        "unmatched_uploads": unmatched,
        "critical_missing_uploads": critical_missing,
    }
    out = evidence_root() / "security" / "security_workflow_artifact_coverage_validator.json"
    write_json_report(out, report)
    print(f"SECURITY_WORKFLOW_ARTIFACT_COVERAGE_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
