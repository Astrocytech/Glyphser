#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    root = evidence_root()
    conformance_result = _read_json(root / "conformance" / "results" / "latest.json")
    conformance_report = _read_json(root / "conformance" / "reports" / "latest.json")
    security_gate = _read_json(root / "security" / "evidence_attestation_gate.json")
    policy_gate = _read_json(root / "security" / "policy_signature.json")

    findings: list[str] = []
    conformance_status = str(conformance_result.get("status", "")).upper() or str(conformance_report.get("status", "")).upper()
    security_status = str(security_gate.get("status", "")).upper()
    policy_status = str(policy_gate.get("status", "")).upper()

    if not conformance_status:
        conformance_status = "MISSING"
    if not security_status:
        findings.append("missing_security_attestation_status")
    if not policy_status:
        findings.append("missing_policy_signature_status")
    if conformance_status == "PASS" and security_status != "PASS":
        findings.append("conformance_pass_but_security_attestation_failed")
    if conformance_status == "PASS" and policy_status != "PASS":
        findings.append("conformance_pass_but_policy_signature_failed")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "conformance_status": conformance_status,
            "security_attestation_status": security_status,
            "policy_signature_status": policy_status,
        },
        "metadata": {"gate": "conformance_security_coupling"},
    }
    out = root / "security" / "conformance_security_coupling.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CONFORMANCE_SECURITY_COUPLING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
