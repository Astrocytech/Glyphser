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

REQUIRED = ["status"]
REQUIRED_NORMALIZED = ["findings", "summary", "metadata", "schema_version"]
IGNORE = {"security_slo_history.json"}
ALLOWED_STATUS = {"PASS", "FAIL", "WARN", "SKIP"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    strict = os.environ.get("GLYPHSER_SECURITY_SCHEMA_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}
    sec = evidence_root() / "security"
    findings: list[str] = []
    scanned = 0
    normalized = 0
    for path in sorted(sec.glob("*.json")):
        if path.name in IGNORE:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_json:{path.name}")
            continue
        if not isinstance(payload, dict):
            findings.append(f"invalid_payload:{path.name}")
            continue
        # Only normalize report-like payloads; security artifacts like SBOM/provenance
        # are JSON documents but not gate reports and follow separate schemas.
        if "status" not in payload:
            continue
        scanned += 1
        is_normalized = True
        status = str(payload.get("status", "")).upper()
        if status not in ALLOWED_STATUS:
            findings.append(f"invalid_status:{path.name}")
        for key in REQUIRED:
            if key not in payload:
                findings.append(f"missing_{key}:{path.name}")
                is_normalized = False
        for key in REQUIRED_NORMALIZED:
            if key not in payload:
                is_normalized = False
                if strict:
                    findings.append(f"missing_{key}:{path.name}")
        if is_normalized:
            normalized += 1

    normalization_pct = 100.0 if scanned == 0 else (normalized / scanned) * 100.0
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_files": scanned,
            "required_keys": REQUIRED,
            "required_normalized_keys": REQUIRED_NORMALIZED,
            "normalized_files": normalized,
            "normalization_pct": round(normalization_pct, 2),
            "strict_mode": strict,
        },
        "metadata": {"gate": "security_schema_normalization_gate"},
    }
    out = sec / "security_schema_normalization_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SCHEMA_NORMALIZATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
