#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.quality_gates.telemetry import emit_gate_trace

OUT = ROOT / "evidence" / "gates" / "quality" / "module_coverage.json"

THRESHOLDS = {
    "glyphser/public": 80.0,
    "tooling/release": 70.0,
    "tooling/quality_gates": 70.0,
}


def _matches_prefix(filename: str, prefix: str) -> bool:
    # Coverage XML may contain relative paths (glyphser/public/...)
    # or absolute paths (.../Glyphser/glyphser/public/...).
    norm = filename.replace("\\", "/").lstrip("./")
    return (
        norm == prefix
        or norm.startswith(prefix + "/")
        or f"/{prefix}/" in norm
    )


def evaluate(coverage_file: Path) -> dict:
    if not coverage_file.exists():
        payload = {"status": "FAIL", "findings": [f"missing_coverage_file:{coverage_file}"]}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(ROOT, "module_coverage", payload)
        return payload

    tree = ET.parse(coverage_file)
    root = tree.getroot()

    totals = {k: {"covered": 0, "valid": 0} for k in THRESHOLDS}
    for cls in root.findall(".//class"):
        filename = cls.attrib.get("filename", "")
        for prefix in THRESHOLDS:
            if _matches_prefix(filename, prefix):
                lines = cls.find("lines")
                if lines is None:
                    continue
                for ln in lines.findall("line"):
                    totals[prefix]["valid"] += 1
                    if int(ln.attrib.get("hits", "0")) > 0:
                        totals[prefix]["covered"] += 1

    findings = []
    summary = {}
    for prefix, data in totals.items():
        valid = data["valid"]
        covered = data["covered"]
        ratio = (covered / valid * 100.0) if valid else 0.0
        summary[prefix] = {
            "covered_lines": covered,
            "valid_lines": valid,
            "coverage_percent": round(ratio, 2),
            "minimum_percent": THRESHOLDS[prefix],
        }
        if valid == 0:
            findings.append(f"no_covered_lines_for_prefix:{prefix}")
        elif ratio < THRESHOLDS[prefix]:
            findings.append(f"coverage_below_threshold:{prefix}:{ratio:.2f}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "module_coverage", payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce per-module coverage minimums")
    parser.add_argument("--coverage-file", default="coverage.xml")
    args = parser.parse_args()

    report = evaluate(Path(args.coverage_file))
    if report["status"] == "PASS":
        print("MODULE_COVERAGE_GATE: PASS")
        return 0
    print("MODULE_COVERAGE_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
