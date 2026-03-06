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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DRILL = ROOT / "governance" / "security" / "branch_protection_api_unavailability_drill.json"


def _verify_signed_json(path: Path, findings: list[str]) -> dict[str, Any]:
    if not path.exists():
        findings.append("missing_branch_protection_api_unavailability_drill")
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    sig_path = path.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append("missing_branch_protection_api_unavailability_drill_signature")
    else:
        sig = sig_path.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(path, sig, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(path, sig, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_branch_protection_api_unavailability_drill_signature")
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = _verify_signed_json(DRILL, findings)

    status = str(payload.get("status", "")).upper()
    if status != "PASS":
        findings.append(f"drill_not_passed:{status or 'MISSING'}")

    incident_id = str(payload.get("incident_id", "")).strip()
    if not incident_id:
        findings.append("missing_incident_id")

    simulated_error = str(payload.get("simulated_api_error", "")).strip()
    if not simulated_error:
        findings.append("missing_simulated_api_error")

    expected_gate_behavior = str(payload.get("expected_gate_behavior", "")).strip()
    if not expected_gate_behavior:
        findings.append("missing_expected_gate_behavior")

    observed_gate_status = str(payload.get("observed_gate_status", "")).upper().strip()
    if observed_gate_status != "FAIL":
        findings.append(f"invalid_observed_gate_status:{observed_gate_status or 'MISSING'}")

    fail_closed = bool(payload.get("fail_closed", False))
    if not fail_closed:
        findings.append("gate_did_not_fail_closed")

    emitted_evidence = str(payload.get("emitted_evidence", "")).strip()
    if not emitted_evidence:
        findings.append("missing_emitted_evidence")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "incident_id": incident_id,
            "simulated_api_error": simulated_error,
            "observed_gate_status": observed_gate_status,
            "fail_closed": fail_closed,
            "emitted_evidence": emitted_evidence,
        },
        "metadata": {"gate": "branch_protection_api_unavailability_drill"},
    }
    out = evidence_root() / "security" / "branch_protection_api_unavailability_drill.json"
    write_json_report(out, report)
    print(f"BRANCH_PROTECTION_API_UNAVAILABILITY_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
