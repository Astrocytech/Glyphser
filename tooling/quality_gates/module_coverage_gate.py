#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from defusedxml import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "evidence" / "gates" / "quality" / "module_coverage.json"

MODULE_TARGETS = {
    "public_api": {
        "minimum_percent": 80.0,
        "prefixes": ["glyphser/public", "glyphser/__init__.py", "public"],
    },
}


def _matches_prefix(filename: str, prefix: str) -> bool:
    # Coverage XML may contain relative paths (glyphser/public/...)
    # or absolute paths (.../Glyphser/glyphser/public/...).
    norm = filename.replace("\\", "/").lstrip("./")
    if "." in prefix.split("/")[-1]:
        # File target.
        return norm == prefix or norm.endswith("/" + prefix)
    return norm == prefix or norm.startswith(prefix + "/") or f"/{prefix}/" in norm


def evaluate(coverage_file: Path) -> dict:
    from tooling.quality_gates.telemetry import emit_gate_trace

    if not coverage_file.exists():
        payload = {
            "status": "FAIL",
            "findings": [f"missing_coverage_file:{coverage_file}"],
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(ROOT, "module_coverage", payload)
        return payload

    tree = ET.parse(coverage_file)
    root = tree.getroot()

    totals = {k: {"covered": 0, "valid": 0} for k in MODULE_TARGETS}
    for pkg in root.findall(".//package"):
        pkg_name = pkg.attrib.get("name", "").replace(".", "/")
        for cls in pkg.findall(".//class"):
            filename = cls.attrib.get("filename", "")
            candidates = {filename}
            if pkg_name:
                candidates.add(f"{pkg_name}/{filename}")
                # Some coverage emitters provide package= glyphser and filename=public/foo.py.
                # Keep a glyphser-rooted candidate to make prefix matching stable.
                if not filename.startswith(pkg_name + "/"):
                    candidates.add(f"{pkg_name}/{filename.lstrip('/')}")
            for target, cfg in MODULE_TARGETS.items():
                if any(_matches_prefix(candidate, prefix) for candidate in candidates for prefix in cfg["prefixes"]):
                    lines = cls.find("lines")
                    if lines is None:
                        continue
                    for ln in lines.findall("line"):
                        totals[target]["valid"] += 1
                        if int(ln.attrib.get("hits", "0")) > 0:
                            totals[target]["covered"] += 1

    findings = []
    summary = {}
    for target, data in totals.items():
        valid = data["valid"]
        covered = data["covered"]
        ratio = (covered / valid * 100.0) if valid else 0.0
        minimum = float(MODULE_TARGETS[target]["minimum_percent"])
        summary[target] = {
            "covered_lines": covered,
            "valid_lines": valid,
            "coverage_percent": round(ratio, 2),
            "minimum_percent": minimum,
            "prefixes": MODULE_TARGETS[target]["prefixes"],
        }
        if valid == 0:
            findings.append(f"no_covered_lines_for_target:{target}")
        elif ratio < minimum:
            findings.append(f"coverage_below_threshold:{target}:{ratio:.2f}")

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
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
