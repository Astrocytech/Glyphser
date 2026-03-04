#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXEMPT_FILES = {
    "security_exception_suppression_gate.py",
}


def _is_broad_handler(node: ast.ExceptHandler) -> bool:
    if node.type is None:
        return True
    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
        return True
    return False


def _is_suppressive_body(body: list[ast.stmt]) -> bool:
    if not body:
        return True
    if len(body) == 1 and isinstance(body[0], ast.Pass):
        return True
    if len(body) == 1 and isinstance(body[0], ast.Continue):
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_files = 0

    for path in sorted((ROOT / "tooling" / "security").glob("*.py")):
        if path.name in EXEMPT_FILES:
            continue
        checked_files += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"parse_error:{path.name}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                if not _is_broad_handler(handler):
                    continue
                if _is_suppressive_body(handler.body):
                    findings.append(f"broad_exception_suppression:{path.name}:{handler.lineno}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_files": checked_files, "findings": len(findings)},
        "metadata": {"gate": "security_exception_suppression_gate"},
    }
    out = evidence_root() / "security" / "security_exception_suppression_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_EXCEPTION_SUPPRESSION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
