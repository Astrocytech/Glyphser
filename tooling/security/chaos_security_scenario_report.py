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


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _status(sec: Path, name: str) -> str:
    path = sec / name
    if not path.exists():
        return "MISSING"
    payload = _load_json(path)
    return str(payload.get("status", "UNKNOWN")).upper()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    scenarios: list[dict[str, Any]] = []

    install_report_exists = (sec / "security_toolchain_install_report.json").exists()
    toolchain_gate_status = _status(sec, "security_toolchain_gate.json")
    network_validated = (not install_report_exists) and toolchain_gate_status == "FAIL"
    network_evidence = toolchain_gate_status != "MISSING"
    scenarios.append(
        {
            "id": "network_outage_tool_install_fail_safe",
            "evidence_present": network_evidence,
            "validated": network_validated,
            "observed": {
                "security_toolchain_install_report_present": install_report_exists,
                "security_toolchain_gate_status": toolchain_gate_status,
            },
        }
    )

    upload_gate_status = _status(sec, "upload_manifest_completeness_gate.json")
    partial_upload_validated = upload_gate_status == "FAIL"
    partial_upload_evidence = upload_gate_status != "MISSING"
    scenarios.append(
        {
            "id": "partial_artifact_upload_detection",
            "evidence_present": partial_upload_evidence,
            "validated": partial_upload_validated,
            "observed": {"upload_manifest_completeness_gate_status": upload_gate_status},
        }
    )

    attestation_status = _status(sec, "evidence_attestation_gate.json")
    provenance_status = _status(sec, "provenance_signature_gate.json")
    envelope_status = _status(sec, "integrity_envelope_gate.json")
    corrupted_sig_validated = any(x == "FAIL" for x in (attestation_status, provenance_status, envelope_status))
    corrupted_sig_evidence = any(x != "MISSING" for x in (attestation_status, provenance_status, envelope_status))
    scenarios.append(
        {
            "id": "corrupted_signatures_and_attestations_detection",
            "evidence_present": corrupted_sig_evidence,
            "validated": corrupted_sig_validated,
            "observed": {
                "evidence_attestation_gate_status": attestation_status,
                "provenance_signature_gate_status": provenance_status,
                "integrity_envelope_gate_status": envelope_status,
            },
        }
    )

    for scenario in scenarios:
        sid = str(scenario.get("id", ""))
        evidence_present = bool(scenario.get("evidence_present"))
        validated = bool(scenario.get("validated"))
        if evidence_present and not validated:
            findings.append(f"chaos_scenario_failed:{sid}")
        if not evidence_present:
            findings.append(f"chaos_scenario_missing_evidence:{sid}")

    if any(item.startswith("chaos_scenario_failed:") for item in findings):
        status = "FAIL"
    elif findings:
        status = "WARN"
    else:
        status = "PASS"

    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "scenarios_total": len(scenarios),
            "scenarios_validated": sum(1 for item in scenarios if item.get("validated") is True),
            "scenarios_missing_evidence": sum(1 for item in scenarios if not item.get("evidence_present")),
        },
        "metadata": {"gate": "chaos_security_scenario_report"},
        "scenarios": scenarios,
    }
    out = sec / "chaos_security_scenario_report.json"
    write_json_report(out, report)
    print(f"CHAOS_SECURITY_SCENARIO_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
