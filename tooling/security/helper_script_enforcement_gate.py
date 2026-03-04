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

SECURITY_DIR = ROOT / "tooling" / "security"
FORCED_SUCCESS_RE = re.compile(r"SystemExit\(\s*0\s*\)")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    for path in sorted(SECURITY_DIR.glob("*.py")):
        checked += 1
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if "except Exception:\n        pass" in text:
            findings.append(f"except_pass_pattern:{rel}")
        if "except Exception:\n        continue" in text:
            findings.append(f"except_continue_pattern:{rel}")
        if FORCED_SUCCESS_RE.search(text):
            findings.append(f"forced_success_exit:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_scripts": checked},
        "metadata": {"gate": "helper_script_enforcement_gate"},
    }
    out = evidence_root() / "security" / "helper_script_enforcement_gate.json"
    write_json_report(out, report)
    print(f"HELPER_SCRIPT_ENFORCEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
