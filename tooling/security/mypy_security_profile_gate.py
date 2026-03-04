#!/usr/bin/env python3
from __future__ import annotations

import configparser
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

REQUIRED = {
    "disallow_untyped_defs": "True",
    "disallow_incomplete_defs": "True",
    "warn_return_any": "True",
}

TARGET_SECTIONS = [
    "mypy-tooling.security.*",
    "mypy-runtime.glyphser.security.*",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    config_path = ROOT / "mypy.ini"
    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")

    findings: list[str] = []
    for section in TARGET_SECTIONS:
        if section not in parser:
            findings.append(f"missing_section:{section}")
            continue
        for key, expected in REQUIRED.items():
            got = parser[section].get(key, "").strip()
            if got != expected:
                findings.append(f"invalid_setting:{section}:{key}:{got or 'missing'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"config": str(config_path.relative_to(ROOT)), "target_sections": TARGET_SECTIONS},
        "metadata": {"gate": "mypy_security_profile_gate"},
    }
    out = evidence_root() / "security" / "mypy_security_profile_gate.json"
    write_json_report(out, report)
    print(f"MYPY_SECURITY_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
