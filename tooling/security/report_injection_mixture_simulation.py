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

SCENARIO_PATH = ROOT / "governance" / "security" / "report_injection_mixture_simulation.json"


def _load(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_report_injection_scenario_file"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_report_injection_scenario_file"
    rows = payload.get("scenarios", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return [], "invalid_report_injection_scenario_schema"
    return [row for row in rows if isinstance(row, dict)], ""


def _detect(payload: dict[str, Any]) -> bool:
    source = str(payload.get("source", "")).strip().lower()
    signature_ok = bool(payload.get("signature_valid", False))
    schema_ok = bool(payload.get("schema_valid", False))
    if source not in {"trusted", "pipeline"}:
        return True
    if not signature_ok:
        return True
    if not schema_ok:
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scenarios, load_err = _load(SCENARIO_PATH)
    if load_err:
        findings.append(load_err)

    results: list[dict[str, Any]] = []
    for idx, scenario in enumerate(scenarios):
        sid = str(scenario.get("id", "")).strip() or f"scenario-{idx}"
        expected_detection = bool(scenario.get("expected_detection", True))
        payload = scenario.get("report", {})
        detected = _detect(payload if isinstance(payload, dict) else {})
        if detected != expected_detection:
            findings.append(f"report_injection_simulation_mismatch:{sid}")
        results.append(
            {
                "id": sid,
                "expected_detection": expected_detection,
                "detected": detected,
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scenario_file": str(SCENARIO_PATH),
            "total_scenarios": len(results),
            "mismatches": sum(1 for item in results if item.get("expected_detection") != item.get("detected")),
        },
        "metadata": {"gate": "report_injection_mixture_simulation"},
        "scenarios": results,
    }
    out = evidence_root() / "security" / "report_injection_mixture_simulation.json"
    write_json_report(out, report)
    print(f"REPORT_INJECTION_MIXTURE_SIMULATION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
