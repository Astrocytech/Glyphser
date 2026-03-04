#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

REQUIRED = ["status", "findings", "summary", "metadata"]
IGNORE = {"security_slo_history.json"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    scanned = 0
    for path in sorted(sec.glob("*.json")):
        if path.name in IGNORE:
            continue
        scanned += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_json:{path.name}")
            continue
        if not isinstance(payload, dict):
            findings.append(f"invalid_payload:{path.name}")
            continue
        for key in REQUIRED:
            if key not in payload:
                findings.append(f"missing_{key}:{path.name}")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_files": scanned, "required_keys": REQUIRED},
        "metadata": {"gate": "security_schema_normalization_gate"},
    }
    out = sec / "security_schema_normalization_gate.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SCHEMA_NORMALIZATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
