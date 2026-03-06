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

DRILL = ROOT / "governance" / "security" / "partial_evidence_corruption_incident_response_drill.json"


def _verify_signed_json(path: Path, findings: list[str]) -> dict[str, Any]:
    if not path.exists():
        findings.append("missing_partial_evidence_corruption_incident_response_drill")
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    sig_path = path.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append("missing_partial_evidence_corruption_incident_response_drill_signature")
    else:
        sig = sig_path.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(path, sig, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(path, sig, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_partial_evidence_corruption_incident_response_drill_signature")
    return payload if isinstance(payload, dict) else {}


def _str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


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

    corrupted_artifacts = _str_list(payload.get("corrupted_artifacts", []))
    if not corrupted_artifacts:
        findings.append("missing_corrupted_artifacts")

    detection_method = str(payload.get("detection_method", "")).strip()
    if not detection_method:
        findings.append("missing_detection_method")

    containment_actions = _str_list(payload.get("containment_actions", []))
    if not containment_actions:
        findings.append("missing_containment_actions")

    recovery_steps = _str_list(payload.get("recovery_steps", []))
    if not recovery_steps:
        findings.append("missing_recovery_steps")

    fallback_verification = bool(payload.get("fallback_verification_completed", False))
    if not fallback_verification:
        findings.append("fallback_verification_not_completed")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "incident_id": incident_id,
            "corrupted_artifact_count": len(corrupted_artifacts),
            "containment_actions": len(containment_actions),
            "recovery_steps": len(recovery_steps),
            "fallback_verification_completed": fallback_verification,
        },
        "metadata": {"gate": "partial_evidence_corruption_incident_response_drill"},
    }
    out = evidence_root() / "security" / "partial_evidence_corruption_incident_response_drill.json"
    write_json_report(out, report)
    print(f"PARTIAL_EVIDENCE_CORRUPTION_INCIDENT_RESPONSE_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
