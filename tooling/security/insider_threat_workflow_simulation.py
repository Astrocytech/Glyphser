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

SCENARIO_PATH = ROOT / "governance" / "security" / "insider_threat_workflow_simulation.json"

_PERM_WIDENING = re.compile(r"permissions:\s*\n(?:[^\n]*\n)*?\s*contents:\s*write", re.IGNORECASE)
_PIN_REMOVAL = re.compile(r"uses:\s*[^@\n]+(?:\n|$)", re.IGNORECASE)
_BYPASS_ATTEMPT = re.compile(r"if:\s*(?:true|1|always\(\))", re.IGNORECASE)


def _load_scenarios(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_insider_threat_scenario_file"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_insider_threat_scenario_file"
    rows = payload.get("scenarios", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return [], "invalid_insider_threat_scenario_schema"
    return [row for row in rows if isinstance(row, dict)], ""


def _detected(kind: str, workflow_text: str) -> bool:
    if kind == "permission_widening":
        return bool(_PERM_WIDENING.search(workflow_text))
    if kind == "pin_removal":
        return bool(_PIN_REMOVAL.search(workflow_text))
    if kind == "gate_bypass":
        return bool(_BYPASS_ATTEMPT.search(workflow_text))
    return False


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scenarios, load_err = _load_scenarios(SCENARIO_PATH)
    if load_err:
        findings.append(load_err)

    results: list[dict[str, Any]] = []
    for idx, scenario in enumerate(scenarios):
        sid = str(scenario.get("id", "")).strip() or f"scenario-{idx}"
        kind = str(scenario.get("kind", "")).strip()
        workflow_text = str(scenario.get("mutated_workflow", ""))
        expected_detection = bool(scenario.get("expected_detection", True))
        got = _detected(kind, workflow_text)
        if got != expected_detection:
            findings.append(f"simulation_mismatch:{sid}")
        results.append(
            {
                "id": sid,
                "kind": kind,
                "expected_detection": expected_detection,
                "detected": got,
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scenario_file": str(SCENARIO_PATH),
            "total_scenarios": len(results),
            "detected_scenarios": sum(1 for row in results if row.get("detected")),
            "mismatches": sum(1 for row in results if row.get("expected_detection") != row.get("detected")),
        },
        "metadata": {"gate": "insider_threat_workflow_simulation"},
        "scenarios": results,
    }
    out = evidence_root() / "security" / "insider_threat_workflow_simulation.json"
    write_json_report(out, report)
    print(f"INSIDER_THREAT_WORKFLOW_SIMULATION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
