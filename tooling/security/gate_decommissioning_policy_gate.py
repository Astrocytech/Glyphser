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

POLICY = ROOT / "governance" / "security" / "gate_decommissioning_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_gate_decommissioning_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_gate_decommissioning_policy")

    records = policy.get("decommission_records", []) if isinstance(policy, dict) else []
    if not isinstance(records, list):
        records = []
        findings.append("invalid_decommission_records")

    checked = 0
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            findings.append(f"invalid_decommission_record:{idx}")
            continue
        checked += 1
        obsolete = str(record.get("obsolete_gate", "")).strip()
        replacement = str(record.get("replacement_gate", "")).strip()
        proof = str(record.get("replacement_proof_artifact", "")).strip()
        if not obsolete:
            findings.append(f"missing_obsolete_gate:{idx}")
        if not replacement:
            findings.append(f"missing_replacement_gate:{idx}")
        if not proof:
            findings.append(f"missing_replacement_proof_artifact:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"decommission_records": len(records), "validated_records": checked},
        "metadata": {"gate": "gate_decommissioning_policy_gate"},
    }
    out = evidence_root() / "security" / "gate_decommissioning_policy_gate.json"
    write_json_report(out, report)
    print(f"GATE_DECOMMISSIONING_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
