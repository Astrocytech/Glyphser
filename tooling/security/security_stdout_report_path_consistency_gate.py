#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

SECURITY_TOOLING = ROOT / "tooling" / "security"
WRITE_VAR_RE = re.compile(r"write_json_report\(\s*(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*,")
PRINT_VAR_RE = re.compile(r"print\(f\"[^\"]*\{(?P<var>[A-Za-z_][A-Za-z0-9_]*)\}[^\"]*\"\)")


def _candidate_gate_paths() -> list[Path]:
    if not SECURITY_TOOLING.exists():
        return []
    return sorted(
        path
        for path in SECURITY_TOOLING.glob("*.py")
        if path.name.endswith("_gate.py") and path.name != "security_stdout_report_path_consistency_gate.py"
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0

    for path in _candidate_gate_paths():
        checked += 1
        text = path.read_text(encoding="utf-8")
        write_vars = {m.group("var") for m in WRITE_VAR_RE.finditer(text)}
        print_vars = {m.group("var") for m in PRINT_VAR_RE.finditer(text)}
        if not write_vars:
            findings.append(f"missing_write_json_report_call:{path.name}")
            continue
        if not any(var in print_vars for var in write_vars):
            findings.append(f"stdout_report_path_mismatch:{path.name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "gates_checked": checked,
            "gates_failed": len(findings),
        },
        "metadata": {"gate": "security_stdout_report_path_consistency_gate"},
    }
    out = evidence_root() / "security" / "security_stdout_report_path_consistency_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_STDOUT_REPORT_PATH_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
