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

LOCKFILE = ROOT / "requirements.lock"
SECURITY_TOOLS = ("bandit", "pip-audit", "semgrep", "setuptools")
REQ_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s]+)")
HASH_RE = re.compile(r"--hash=sha256:[0-9a-fA-F]{64}")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not LOCKFILE.exists():
        findings.append("missing_requirements_lock")
        lines: list[str] = []
    else:
        lines = LOCKFILE.read_text(encoding="utf-8").splitlines()

    seen_tools: set[str] = set()
    hashed_tools: set[str] = set()

    current_pkg = ""
    saw_hash = False
    for raw in lines + [""]:
        line = raw.strip()
        m = REQ_RE.match(line)
        if m:
            if current_pkg and current_pkg in SECURITY_TOOLS:
                seen_tools.add(current_pkg)
                if saw_hash:
                    hashed_tools.add(current_pkg)
            current_pkg = m.group(1).lower()
            saw_hash = bool(HASH_RE.search(line))
            continue
        if current_pkg and HASH_RE.search(line):
            saw_hash = True
        if current_pkg and (not line or (line and not raw.startswith(" ") and not raw.startswith("\t") and not raw.startswith("-"))):
            if current_pkg in SECURITY_TOOLS:
                seen_tools.add(current_pkg)
                if saw_hash:
                    hashed_tools.add(current_pkg)
            current_pkg = ""
            saw_hash = False

    for tool in SECURITY_TOOLS:
        if tool not in seen_tools:
            findings.append(f"missing_security_tool_in_lockfile:{tool}")
        elif tool not in hashed_tools:
            findings.append(f"missing_transitive_hash_provenance:{tool}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lockfile": str(LOCKFILE.relative_to(ROOT)).replace("\\", "/"),
            "security_tools_expected": len(SECURITY_TOOLS),
            "security_tools_seen": len(seen_tools),
            "security_tools_with_hash_provenance": len(hashed_tools),
        },
        "metadata": {"gate": "lockfile_transitive_provenance_gate"},
    }
    out = evidence_root() / "security" / "lockfile_transitive_provenance_gate.json"
    write_json_report(out, report)
    print(f"LOCKFILE_TRANSITIVE_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
