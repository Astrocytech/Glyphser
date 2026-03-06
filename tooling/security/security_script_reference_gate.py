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

SECURITY_DIR = ROOT / "tooling" / "security"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
POLICY = ROOT / "governance" / "security" / "security_script_reference_policy.json"
BASELINE = ROOT / "governance" / "security" / "security_script_reference_baseline.json"
SCRIPT_RE = re.compile(r"tooling/security/[A-Za-z0-9_.\-/]+\.py")


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid_object:{path}")
    return payload


def _collect_security_scripts() -> set[str]:
    scripts: set[str] = set()
    for path in sorted(SECURITY_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        scripts.add(str(path.relative_to(ROOT)).replace("\\", "/"))
    return scripts


def _collect_workflow_references() -> set[str]:
    references: set[str] = set()
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        references.update(match.group(0) for match in SCRIPT_RE.finditer(text))
    return references


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not BASELINE.exists():
        findings.append(f"missing_baseline:{BASELINE.relative_to(ROOT).as_posix()}")
    if not POLICY.exists():
        findings.append(f"missing_policy:{POLICY.relative_to(ROOT).as_posix()}")

    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {
                "new_scripts": 0,
                "referenced_new_scripts": 0,
                "archived_new_scripts": 0,
                "archived_scripts_still_wired": 0,
            },
            "metadata": {"gate": "security_script_reference_gate"},
        }
        out = evidence_root() / "security" / "security_script_reference_gate.json"
        write_json_report(out, report)
        print(f"SECURITY_SCRIPT_REFERENCE_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    baseline = _load_json_object(BASELINE)
    policy = _load_json_object(POLICY)

    known_scripts = {
        str(item).strip()
        for item in baseline.get("known_scripts", [])
        if isinstance(item, str) and str(item).strip()
    }
    archived_scripts = {
        str(item).strip()
        for item in policy.get("archived_scripts", [])
        if isinstance(item, str) and str(item).strip()
    }

    current_scripts = _collect_security_scripts()
    workflow_refs = _collect_workflow_references()

    new_scripts = sorted(current_scripts - known_scripts)
    referenced_new = [script for script in new_scripts if script in workflow_refs]
    archived_new = [script for script in new_scripts if script in archived_scripts]
    archived_referenced = [script for script in sorted(archived_scripts) if script in workflow_refs]

    for script in new_scripts:
        if script not in workflow_refs and script not in archived_scripts:
            findings.append(f"unreferenced_new_security_script:{script}")
    for script in archived_referenced:
        findings.append(f"archived_script_still_wired:{script}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "new_scripts": len(new_scripts),
            "referenced_new_scripts": len(referenced_new),
            "archived_new_scripts": len(archived_new),
            "archived_scripts_still_wired": len(archived_referenced),
        },
        "metadata": {
            "gate": "security_script_reference_gate",
            "baseline_path": str(BASELINE.relative_to(ROOT)).replace("\\", "/"),
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out = evidence_root() / "security" / "security_script_reference_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SCRIPT_REFERENCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
