#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

SCAN_CALLS = {"glob", "rglob", "iterdir", "listdir"}


def _is_sorted_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sorted"


def _iterates_scan_call(node: ast.AST) -> tuple[bool, str]:
    if not isinstance(node, ast.Call):
        return False, ""
    if isinstance(node.func, ast.Attribute) and node.func.attr in SCAN_CALLS:
        return True, node.func.attr
    if isinstance(node.func, ast.Name) and node.func.id in SCAN_CALLS:
        return True, node.func.id
    return False, ""


def _check_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        return [f"parse_error:{rel}:{type(exc).__name__}"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        iterator = node.iter
        if _is_sorted_call(iterator):
            continue
        is_scan, call_name = _iterates_scan_call(iterator)
        if not is_scan:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        findings.append(f"unsorted_scan_iteration:{rel}:{node.lineno}:{call_name}")
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    security_dir = ROOT / "tooling" / "security"
    findings: list[str] = []
    checked_files = 0
    for path in sorted(security_dir.glob("*_gate.py")):
        checked_files += 1
        findings.extend(_check_file(path))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_files": checked_files, "findings": len(findings)},
        "metadata": {"gate": "security_scan_ordering_gate"},
    }
    out = evidence_root() / "security" / "security_scan_ordering_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SCAN_ORDERING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
