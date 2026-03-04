#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file, verify_file
from tooling.lib.path_config import evidence_root
from tooling.security.stage_s_policy import load_stage_s_policy

ROOT = Path(__file__).resolve().parents[2]


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

    sig = drill_path.with_suffix(drill_path.suffix + ".sig")
    if drill_path.exists() and not sig.exists():
        sig.write_text(sign_file(drill_path, key=current_key(strict=False)) + "\n", encoding="utf-8")
    if drill_path.exists() and sig.exists():
        if not verify_file(drill_path, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False)):
            findings.append("drill_signature_invalid")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"drill_path": str(drill_path.relative_to(ROOT)).replace('\\', '/')},
        "metadata": {"gate": "disaster_recovery_drill_gate"},
    }
    out = evidence_root() / "security" / "disaster_recovery_drill_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DISASTER_RECOVERY_DRILL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
