#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

DEPENDENCY_POLICY = ROOT / "governance" / "security" / "security_gate_dependency_policy.json"
BACKUP_POLICY = ROOT / "governance" / "security" / "critical_control_backup_policy.json"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    dep_payload = _load_json(DEPENDENCY_POLICY)
    backup_payload = _load_json(BACKUP_POLICY)
    dep_controls = dep_payload.get("critical_controls", [])
    backup_controls = backup_payload.get("controls", [])

    if not isinstance(dep_controls, list):
        raise ValueError("security_gate_dependency_policy.json critical_controls must be a list")
    if not isinstance(backup_controls, list):
        raise ValueError("critical_control_backup_policy.json controls must be a list")

    by_control: dict[str, dict[str, object]] = {}
    for item in dep_controls:
        if not isinstance(item, dict):
            continue
        control_id = str(item.get("control_id", "")).strip()
        if not control_id:
            continue
        verifiers = sorted({str(v).strip() for v in item.get("verifiers", []) if str(v).strip()})
        required = max(int(item.get("required_redundant_verifiers", 2)), 1)
        by_control[control_id] = {
            "control_id": control_id,
            "required_verifiers": required,
            "dependency_policy_verifiers": verifiers,
            "backup_policy_verifiers": [],
        }

    for item in backup_controls:
        if not isinstance(item, dict):
            continue
        control_id = str(item.get("control_id", "")).strip()
        if not control_id:
            continue
        primary = str(item.get("primary_report", "")).strip()
        backups = [str(name).strip() for name in item.get("backup_reports", []) if str(name).strip()]
        entry = by_control.setdefault(
            control_id,
            {
                "control_id": control_id,
                "required_verifiers": 2,
                "dependency_policy_verifiers": [],
                "backup_policy_verifiers": [],
            },
        )
        merged = sorted({primary, *backups} - {""})
        entry["backup_policy_verifiers"] = merged

    report_controls: list[dict[str, object]] = []
    resilient = 0
    for control_id in sorted(by_control):
        entry = by_control[control_id]
        verifiers = sorted(
            {
                *[str(v) for v in entry.get("dependency_policy_verifiers", [])],
                *[str(v) for v in entry.get("backup_policy_verifiers", [])],
            }
        )
        required = int(entry.get("required_verifiers", 2))
        is_resilient = len(verifiers) >= required
        if not is_resilient:
            findings.append(f"insufficient_redundancy:{control_id}:{len(verifiers)}<{required}")
        else:
            resilient += 1
        report_controls.append(
            {
                "control_id": control_id,
                "required_verifiers": required,
                "available_verifiers": verifiers,
                "resilient": is_resilient,
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "controls_total": len(report_controls),
            "controls_resilient": resilient,
            "resilience_ratio": round((resilient / len(report_controls)) if report_controls else 1.0, 4),
        },
        "metadata": {"gate": "critical_control_redundancy_report", "controls": report_controls},
    }
    out = evidence_root() / "security" / "critical_control_redundancy_report.json"
    write_json_report(out, report)
    print(f"CRITICAL_CONTROL_REDUNDANCY_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
