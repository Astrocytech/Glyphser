#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
CATALOG = ROOT / "governance" / "security" / "incident_regression_catalog.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    incidents: list[dict[str, Any]] = []

    if not CATALOG.exists():
        findings.append("missing_incident_regression_catalog")
    else:
        try:
            payload = _load_json(CATALOG)
        except Exception:
            payload = {}
            findings.append("invalid_incident_regression_catalog")
        raw = payload.get("incidents", []) if isinstance(payload, dict) else []
        if not isinstance(raw, list):
            findings.append("invalid_incident_list")
            raw = []
        for idx, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                findings.append(f"invalid_incident_entry:{idx}")
                continue
            incident_id = str(item.get("incident_id", "")).strip()
            controls = item.get("failing_controls", [])
            tests = item.get("regression_tests", [])
            if not incident_id:
                findings.append(f"missing_incident_id:{idx}")
            if not isinstance(controls, list) or not [x for x in controls if isinstance(x, str) and x.strip()]:
                findings.append(f"missing_failing_controls:{idx}")
            if not isinstance(tests, list) or not [x for x in tests if isinstance(x, str) and x.strip()]:
                findings.append(f"missing_regression_tests:{idx}")
            incidents.append(item)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "catalog_path": str(CATALOG.relative_to(ROOT)).replace("\\", "/"),
            "incidents_cataloged": len(incidents),
        },
        "metadata": {"gate": "incident_regression_catalog_gate"},
    }
    out = evidence_root() / "security" / "incident_regression_catalog_gate.json"
    write_json_report(out, report)
    print(f"INCIDENT_REGRESSION_CATALOG_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
