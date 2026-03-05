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

WORKFLOWS_DIR = ROOT / ".github" / "workflows"
HARD_CODED_EVIDENCE_RE = re.compile(r"(?<!GLYPHSER_)evidence/security/")


def _security_workflows() -> list[Path]:
    if not WORKFLOWS_DIR.exists():
        return []
    paths: list[Path] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "tooling/security/" in text or "security" in path.name:
            paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0

    for path in _security_workflows():
        checked += 1
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if "GLYPHSER_EVIDENCE_ROOT" not in text:
            findings.append(f"missing_evidence_root_env_usage:{rel}")
        if HARD_CODED_EVIDENCE_RE.search(text):
            findings.append(f"hardcoded_evidence_security_path:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "security_workflows_checked": checked,
            "violations": len(findings),
        },
        "metadata": {"validator": "security_evidence_root_usage_validator"},
    }
    out = evidence_root() / "security" / "security_evidence_root_usage_validator.json"
    write_json_report(out, report)
    print(f"SECURITY_EVIDENCE_ROOT_USAGE_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
