#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import importlib
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


class Finding(TypedDict):
    file: str
    line: int
    pattern: str


PATTERNS: dict[str, re.Pattern[str]] = {
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_pat": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
}

SCAN_ROOTS: tuple[str, ...] = ("glyphser", "runtime", "tooling", "tests", ".github/workflows")
SKIP_PARTS: tuple[str, ...] = ("__pycache__", ".git", ".venv", "htmlcov", "evidence")


def _scan_file(path: Path, rel: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings
    for idx, line in enumerate(text.splitlines(), start=1):
        for pattern_name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append({"file": rel, "line": idx, "pattern": pattern_name})
    return findings


def _iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        if root.is_file():
            files.append(root)
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(ROOT).parts
            if any(part in SKIP_PARTS for part in rel_parts):
                continue
            files.append(path)
    return sorted(files)


def main() -> int:
    findings: list[Finding] = []
    for path in _iter_scan_files():
        rel = path.relative_to(ROOT).as_posix()
        findings.extend(_scan_file(path, rel))

    status = "PASS" if not findings else "FAIL"
    payload: dict[str, object] = {
        "status": status,
        "finding_count": len(findings),
        "findings": findings,
        "scanned_roots": list(SCAN_ROOTS),
        "summary": {"finding_count": len(findings), "scanned_roots": list(SCAN_ROOTS)},
        "metadata": {"gate": "secret_scan_gate"},
    }
    out = evidence_root() / "security" / "secret_scan.json"
    write_json_report(out, payload)

    print(f"SECRET_SCAN_GATE: {status}")
    print(f"Report: {out}")
    if findings:
        for finding in findings[:25]:
            print(f"{finding['file']}:{finding['line']}:{finding['pattern']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
