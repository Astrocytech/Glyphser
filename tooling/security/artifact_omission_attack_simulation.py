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

SCENARIO_PATH = ROOT / "governance" / "security" / "artifact_omission_attack_simulation.json"


def _load(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_artifact_omission_scenario_file"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_artifact_omission_scenario_file"
    rows = payload.get("scenarios", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return [], "invalid_artifact_omission_scenario_schema"
    return [row for row in rows if isinstance(row, dict)], ""


def _simulate(scenario: dict[str, Any]) -> tuple[bool, str]:
    sid = str(scenario.get("id", "")).strip() or "unknown"
    expected = [str(item).strip() for item in scenario.get("expected_artifacts", []) if str(item).strip()]
    produced = [str(item).strip() for item in scenario.get("produced_artifacts", []) if str(item).strip()]
    expected_detection = bool(scenario.get("expected_detection", True))
    missing = sorted(set(expected) - set(produced))
    detected = bool(missing)
    return detected == expected_detection, f"{sid}:{','.join(missing)}" if missing else sid


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scenarios, load_err = _load(SCENARIO_PATH)
    if load_err:
        findings.append(load_err)

    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        ok, detail = _simulate(scenario)
        if not ok:
            findings.append(f"artifact_omission_simulation_mismatch:{detail}")
        expected = [str(item).strip() for item in scenario.get("expected_artifacts", []) if str(item).strip()]
        produced = [str(item).strip() for item in scenario.get("produced_artifacts", []) if str(item).strip()]
        results.append(
            {
                "id": str(scenario.get("id", "")),
                "expected_detection": bool(scenario.get("expected_detection", True)),
                "detected": bool(sorted(set(expected) - set(produced))),
                "expected_artifact_count": len(expected),
                "produced_artifact_count": len(produced),
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
        "metadata": {"gate": "artifact_omission_attack_simulation"},
        "scenarios": results,
    }
    out = evidence_root() / "security" / "artifact_omission_attack_simulation.json"
    write_json_report(out, report)
    print(f"ARTIFACT_OMISSION_ATTACK_SIMULATION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
