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

EXCLUDED_GATES = {
    "__init__.py",
}


def _covered_by_tests(gate_module: str, tests_dir: Path) -> bool:
    expected_name = tests_dir / f"test_{gate_module}.py"
    if expected_name.exists():
        return True
    pattern = gate_module
    for test_file in sorted(tests_dir.glob("test_*.py")):
        try:
            if pattern in test_file.read_text(encoding="utf-8"):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    security_dir = ROOT / "tooling" / "security"
    tests_dir = ROOT / "tests" / "security"

    gate_modules = sorted(
        p.stem
        for p in sorted(security_dir.glob("*_gate.py"))
        if p.name not in EXCLUDED_GATES
    )
    findings: list[str] = []
    uncovered: list[str] = []

    for gate_module in gate_modules:
        if not _covered_by_tests(gate_module, tests_dir):
            uncovered.append(gate_module)
            findings.append(f"missing_test_coverage:{gate_module}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "total_gates": len(gate_modules),
            "uncovered_gates": len(uncovered),
        },
        "metadata": {
            "gate": "security_gate_test_coverage_gate",
            "tests_dir": str(tests_dir.relative_to(ROOT)).replace("\\", "/"),
        },
        "uncovered": uncovered,
    }
    out = evidence_root() / "security" / "security_gate_test_coverage.json"
    write_json_report(out, report)
    print(f"SECURITY_GATE_TEST_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
