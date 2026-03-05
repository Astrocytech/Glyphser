#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _normalized(path: str) -> str:
    return path.replace("\\", "/")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce coverage threshold for tooling/security/**.")
    parser.add_argument("--coverage-file", default="coverage.xml")
    parser.add_argument("--min-pct", type=float, default=85.0)
    args = parser.parse_args([] if argv is None else argv)

    coverage_path = Path(args.coverage_file)
    findings: list[str] = []
    if not coverage_path.exists():
        findings.append("missing_coverage_file")
        pct = 0.0
        files_count = 0
    else:
        root = ET.parse(coverage_path).getroot()
        lines_valid = 0
        lines_covered = 0
        files_count = 0
        for cls in root.findall(".//class"):
            filename = _normalized(str(cls.attrib.get("filename", "")))
            if not filename.startswith("tooling/security/"):
                continue
            files_count += 1
            for line in cls.findall("./lines/line"):
                hits = int(line.attrib.get("hits", "0"))
                lines_valid += 1
                if hits > 0:
                    lines_covered += 1
        pct = 0.0 if lines_valid == 0 else (lines_covered / lines_valid) * 100.0
        if files_count == 0:
            findings.append("missing_tooling_security_coverage_entries")
        if pct < float(args.min_pct):
            findings.append(f"tooling_security_coverage_below_threshold:{pct:.2f}:{float(args.min_pct):.2f}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "coverage_file": str(coverage_path),
            "tooling_security_coverage_pct": round(pct, 2),
            "minimum_pct": float(args.min_pct),
            "covered_files": files_count,
        },
        "metadata": {"gate": "security_coverage_threshold_gate"},
    }
    out = evidence_root() / "security" / "security_coverage_threshold_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_COVERAGE_THRESHOLD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
