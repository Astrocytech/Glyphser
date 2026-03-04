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

PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)secret[_-]?key\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{4,}"),
    re.compile(r'"(?i:password)"\s*:\s*"[^"]{4,}"'),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
]


def _contains_secret(text: str) -> bool:
    for pat in PATTERNS:
        if pat.search(text):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    scanned = 0
    for path in sorted(sec.glob("*.json")):
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _contains_secret(text):
            findings.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_files": scanned},
        "metadata": {"gate": "report_secret_leak"},
    }
    out = sec / "report_secret_leak.json"
    write_json_report(out, report)
    print(f"REPORT_SECRET_LEAK_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
