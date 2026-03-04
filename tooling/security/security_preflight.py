#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.security.report_io import write_json_report


def _check_tools(strict: bool) -> list[str]:
    findings: list[str] = []
    required = ["python", "git"]
    optional = ["semgrep", "pip-audit", "bandit"]
    for tool in required:
        if shutil.which(tool) is None:
            findings.append(f"missing_required_tool:{tool}")
    if strict:
        for tool in optional:
            if shutil.which(tool) is None:
                findings.append(f"missing_optional_tool_in_strict_mode:{tool}")
    return findings


def _check_env(strict: bool) -> list[str]:
    findings: list[str] = []
    required = ["TZ", "LC_ALL", "LANG"]
    for name in required:
        value = os.environ.get(name, "").strip()
        if not value:
            findings.append(f"missing_env:{name}")
    key = os.environ.get("GLYPHSER_PROVENANCE_HMAC_KEY", "").strip()
    if strict and not key:
        findings.append("missing_env:GLYPHSER_PROVENANCE_HMAC_KEY")
    return findings


def _check_files() -> list[str]:
    findings: list[str] = []
    required_files = [
        ROOT / "governance" / "security" / "policy_signature_manifest.json",
        ROOT / "tooling" / "security" / "security_toolchain_lock.json",
        ROOT / "tooling" / "security" / "security_super_gate_manifest.json",
    ]
    for path in required_files:
        if not path.exists():
            findings.append(f"missing_required_file:{path.relative_to(ROOT).as_posix()}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight validation for local security-gate execution.")
    parser.add_argument("--strict", action="store_true", help="Require full CI-like prerequisites.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args([] if argv is None else argv)

    findings = _check_tools(args.strict) + _check_env(args.strict) + _check_files()
    diagnostics = {
        "missing_required_tool": "Install required tools and ensure they are on PATH.",
        "missing_optional_tool_in_strict_mode": "Install pinned security toolchain via tooling/security/install_security_toolchain.py.",
        "missing_env": "Export required environment variables (TZ, LC_ALL, LANG, GLYPHSER_PROVENANCE_HMAC_KEY in strict mode).",
        "missing_required_file": "Restore missing repository security policy/lock files from version control.",
    }
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"strict": args.strict, "finding_count": len(findings)},
        "metadata": {"tool": "security_preflight"},
        "diagnostics": diagnostics,
    }

    out = ROOT / "evidence" / "security" / "security_preflight.json"
    write_json_report(out, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SECURITY_PREFLIGHT: {report['status']}")
        print(f"Report: {out}")
        if findings:
            for item in findings:
                print(item)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
