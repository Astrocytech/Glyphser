#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    strict_schema = os.environ.get("GLYPHSER_POLICY_SCHEMA_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}
    findings: list[str] = []
    scanned = 0

    for path in sorted((ROOT / "governance" / "security").glob("*.json")):
        scanned += 1
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_json:{rel}")
            continue
        if not isinstance(payload, dict):
            findings.append(f"invalid_shape:{rel}:expected_object")
            continue
        if not payload:
            findings.append(f"invalid_shape:{rel}:empty_object")
        if strict_schema:
            version = payload.get("schema_version")
            if not isinstance(version, int) or version <= 0:
                findings.append(f"missing_or_invalid_schema_version:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_files": scanned, "strict_schema": strict_schema},
        "metadata": {"gate": "policy_schema_validation_gate"},
    }
    out = evidence_root() / "security" / "policy_schema_validation_gate.json"
    write_json_report(out, report)
    print(f"POLICY_SCHEMA_VALIDATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
