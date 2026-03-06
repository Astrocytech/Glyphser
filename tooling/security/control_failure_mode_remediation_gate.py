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

MATRIX = ROOT / "governance" / "security" / "threat_control_matrix.json"
IMMUTABILITY_BASELINE = ROOT / "governance" / "security" / "control_id_immutability_baseline.json"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not MATRIX.exists():
        findings.append("missing_matrix:governance/security/threat_control_matrix.json")
    if not IMMUTABILITY_BASELINE.exists():
        findings.append("missing_immutability_baseline:governance/security/control_id_immutability_baseline.json")
    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {
                "controls_checked": 0,
                "missing_failure_mode": 0,
                "missing_expected_remediation": 0,
                "missing_success_criterion": 0,
                "missing_escalation_path": 0,
                "duplicate_control_ids": 0,
                "added_control_ids": 0,
                "removed_control_ids": 0,
            },
            "metadata": {"gate": "control_failure_mode_remediation_gate"},
        }
        out = evidence_root() / "security" / "control_failure_mode_remediation_gate.json"
        write_json_report(out, report)
        print(f"CONTROL_FAILURE_MODE_REMEDIATION_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    payload = _read_json(MATRIX)
    baseline_payload = _read_json(IMMUTABILITY_BASELINE)
    controls = payload.get("controls", []) if isinstance(payload, dict) else []
    if not isinstance(controls, list):
        controls = []
        findings.append("invalid_controls:not_list")

    missing_failure_mode = 0
    missing_expected_remediation = 0
    missing_success_criterion = 0
    missing_escalation_path = 0
    duplicate_control_ids = 0
    control_ids: list[str] = []

    for idx, raw in enumerate(controls):
        if not isinstance(raw, dict):
            findings.append(f"invalid_control:{idx}:not_object")
            continue
        cid = str(raw.get("id", "")).strip() or f"index_{idx}"
        if cid in control_ids:
            findings.append(f"duplicate_control_id:{cid}")
            duplicate_control_ids += 1
        control_ids.append(cid)
        if not str(raw.get("failure_mode", "")).strip():
            findings.append(f"missing_failure_mode:{cid}")
            missing_failure_mode += 1
        if not str(raw.get("expected_remediation", "")).strip():
            findings.append(f"missing_expected_remediation:{cid}")
            missing_expected_remediation += 1
        if not str(raw.get("success_criterion", "")).strip():
            findings.append(f"missing_success_criterion:{cid}")
            missing_success_criterion += 1
        if not str(raw.get("owner_escalation_path", "")).strip():
            findings.append(f"missing_owner_escalation_path:{cid}")
            missing_escalation_path += 1

    baseline_ids = {
        str(item).strip()
        for item in baseline_payload.get("control_ids", [])
        if isinstance(item, str) and str(item).strip()
    }
    current_ids = set(control_ids)
    added_ids = sorted(current_ids - baseline_ids)
    removed_ids = sorted(baseline_ids - current_ids)
    for cid in added_ids:
        findings.append(f"control_id_added_without_baseline_update:{cid}")
    for cid in removed_ids:
        findings.append(f"control_id_removed_without_baseline_update:{cid}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "controls_checked": len(controls),
            "missing_failure_mode": missing_failure_mode,
            "missing_expected_remediation": missing_expected_remediation,
            "missing_success_criterion": missing_success_criterion,
            "missing_escalation_path": missing_escalation_path,
            "duplicate_control_ids": duplicate_control_ids,
            "added_control_ids": len(added_ids),
            "removed_control_ids": len(removed_ids),
        },
        "metadata": {
            "gate": "control_failure_mode_remediation_gate",
            "matrix_path": str(MATRIX.relative_to(ROOT)).replace("\\", "/"),
            "baseline_path": str(IMMUTABILITY_BASELINE.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out = evidence_root() / "security" / "control_failure_mode_remediation_gate.json"
    write_json_report(out, report)
    print(f"CONTROL_FAILURE_MODE_REMEDIATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
