#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    drill_path = ROOT / str(
        load_stage_s_policy()
        .get("drills", {})
        .get("disaster_recovery_path", "evidence/security/disaster_recovery_drill.json")
    )
    findings: list[str] = []

    if not drill_path.exists():
        findings.append("missing_drill_evidence")
        payload = {}
    else:
        payload = json.loads(drill_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            payload = {}
            findings.append("invalid_drill_payload")

    if payload.get("status") != "PASS":
        findings.append("drill_not_passed")
    for key in ("restored_from_cold_backup", "integrity_verified", "provenance_verified"):
        if payload.get(key) is not True:
            findings.append(f"drill_control_failed:{key}")
    rto_minutes = payload.get("rto_minutes")
    rpo_minutes = payload.get("rpo_minutes")
    if not isinstance(rto_minutes, (int, float)) or float(rto_minutes) < 0:
        findings.append("missing_or_invalid_rto_minutes")
    if not isinstance(rpo_minutes, (int, float)) or float(rpo_minutes) < 0:
        findings.append("missing_or_invalid_rpo_minutes")

    sig = drill_path.with_suffix(drill_path.suffix + ".sig")
    if drill_path.exists() and not sig.exists():
        sig.write_text(sign_file(drill_path, key=current_key(strict=False)) + "\n", encoding="utf-8")
    if drill_path.exists() and sig.exists():
        if not verify_file(drill_path, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False)):
            findings.append("drill_signature_invalid")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "drill_path": str(drill_path.relative_to(ROOT)).replace("\\", "/"),
            "rto_minutes": rto_minutes,
            "rpo_minutes": rpo_minutes,
        },
        "metadata": {"gate": "disaster_recovery_drill_gate"},
    }
    out = evidence_root() / "security" / "disaster_recovery_drill_gate.json"
    write_json_report(out, report)
    print(f"DISASTER_RECOVERY_DRILL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
