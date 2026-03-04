#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"HELPER_SCRIPT_ENFORCEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
