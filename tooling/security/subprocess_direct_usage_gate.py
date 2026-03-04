#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXEMPT_FILES = {"subprocess_policy.py"}
IMPORT_RE = re.compile(r"^\s*(?:import\s+subprocess|from\s+subprocess\s+import\b)")
CALL_RE = re.compile(r"\bsubprocess\.(?:run|Popen|check_output|check_call|call)\(")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0

    for path in sorted((ROOT / "tooling" / "security").glob("*.py")):
        if path.name in EXEMPT_FILES:
            continue
        scanned += 1
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if IMPORT_RE.search(line):
                findings.append(f"direct_subprocess_import:{rel}:{idx}")
            if CALL_RE.search(line):
                findings.append(f"direct_subprocess_call:{rel}:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"files_scanned": scanned, "violations": len(findings)},
        "metadata": {"gate": "subprocess_direct_usage_gate"},
    }
    out = evidence_root() / "security" / "subprocess_direct_usage_gate.json"
    write_json_report(out, report)
    print(f"SUBPROCESS_DIRECT_USAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
