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

TODO = ROOT / "glyphser_security_hardening_master_todo.txt"
DONE_RE = re.compile(r"^DONE\s*$")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    pending_count = 0
    done_marker_present = False

    if not TODO.exists():
        findings.append("missing_hardening_todo")
    else:
        for raw in TODO.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("[ ]"):
                pending_count += 1
            if DONE_RE.match(line):
                done_marker_present = True

    if done_marker_present and pending_count > 0:
        findings.append("done_marker_present_with_unchecked_items")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"pending_count": pending_count, "done_marker_present": done_marker_present},
        "metadata": {"gate": "hardening_pending_count_validator"},
    }
    out = evidence_root() / "security" / "hardening_pending_count_validator.json"
    write_json_report(out, report)
    print(f"HARDENING_PENDING_COUNT_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
