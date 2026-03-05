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
RETURN_STATUS_RE = re.compile(r"return\s+0\s+if\s+report\[\"status\"\].*else\s+1")


def _candidate_gate_paths() -> list[Path]:
    if not SECURITY_TOOLING.exists():
        return []
    return sorted(
        path
        for path in SECURITY_TOOLING.glob("*.py")
        if path.name.endswith("_gate.py") and path.name != "security_status_exitcode_consistency_gate.py"
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0

    for path in _candidate_gate_paths():
        checked += 1
        text = path.read_text(encoding="utf-8")
        if not RETURN_STATUS_RE.search(text):
            findings.append(f"missing_status_exitcode_mapping:{path.name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "gates_checked": checked,
            "gates_failed": len(findings),
        },
        "metadata": {"gate": "security_status_exitcode_consistency_gate"},
    }
    out = evidence_root() / "security" / "security_status_exitcode_consistency_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_STATUS_EXITCODE_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
