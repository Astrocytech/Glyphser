#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WORKFLOWS_DIR = ROOT / ".github" / "workflows"
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MASKING_RE = re.compile(r"\|\|\s*(true|:)\b|;\s*true\b")
SECURITY_CMD_RE = re.compile(r"tooling/security/|semgrep|pip-audit")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_commands = 0

    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for idx, line in enumerate(lines, start=1):
            if "run:" not in line:
                continue
            command = line.split("run:", 1)[1].strip()
            if command.startswith("|") or command.startswith(">"):
                continue
            if not SECURITY_CMD_RE.search(command):
                continue
            checked_commands += 1
            if MASKING_RE.search(command):
                findings.append(f"ambiguous_pass_pattern:{path.relative_to(ROOT).as_posix()}:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_single_line_security_commands": checked_commands},
        "metadata": {"gate": "security_ambiguous_pass_gate"},
    }
    out = evidence_root() / "security" / "security_ambiguous_pass_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_AMBIGUOUS_PASS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
