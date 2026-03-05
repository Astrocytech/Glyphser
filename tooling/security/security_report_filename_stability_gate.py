#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

SECURITY_TOOLING = ROOT / "tooling" / "security"
BASELINE = ROOT / "governance" / "security" / "security_report_filename_baseline.json"
REPORT_PATH_RE = re.compile(r'evidence_root\(\)\s*/\s*"security"\s*/\s*"(?P<name>[^"]+\.json)"')


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _scan_report_names() -> list[str]:
    names: set[str] = set()
    for path in sorted(SECURITY_TOOLING.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in REPORT_PATH_RE.finditer(text):
            names.add(match.group("name"))
    return sorted(names)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    current_names = _scan_report_names()
    if not BASELINE.exists():
        findings.append("missing_security_report_filename_baseline")
        baseline_names: list[str] = []
    else:
        payload = _load_json(BASELINE)
        raw = payload.get("report_filenames", []) if isinstance(payload.get("report_filenames", []), list) else []
        baseline_names = sorted(str(item).strip() for item in raw if str(item).strip())

    current_set = set(current_names)
    baseline_set = set(baseline_names)
    added = sorted(current_set - baseline_set)
    removed = sorted(baseline_set - current_set)

    if added:
        findings.append(f"report_filenames_added:{len(added)}")
    if removed:
        findings.append(f"report_filenames_removed:{len(removed)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "baseline_count": len(baseline_names),
            "current_count": len(current_names),
            "added": len(added),
            "removed": len(removed),
        },
        "metadata": {"gate": "security_report_filename_stability_gate"},
        "added": added,
        "removed": removed,
    }
    out = evidence_root() / "security" / "security_report_filename_stability_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_REPORT_FILENAME_STABILITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
