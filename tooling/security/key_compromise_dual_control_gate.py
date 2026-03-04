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
        .get("key_compromise_path", "evidence/security/key_compromise_drill.json")
    )
    findings: list[str] = []

    payload = json.loads(drill_path.read_text(encoding="utf-8")) if drill_path.exists() else {}
    if not isinstance(payload, dict):
        payload = {}
        findings.append("invalid_drill_payload")

    primary = str(payload.get("primary_approver", "")).strip()
    secondary = str(payload.get("secondary_approver", "")).strip()
    if not primary or not secondary:
        findings.append("missing_dual_control_approvers")
    elif primary == secondary:
        findings.append("approvers_not_distinct")

    if payload.get("rotation_completed") is not True:
        findings.append("rotation_not_completed")
    if payload.get("revocation_list_updated") is not True:
        findings.append("revocation_not_updated")

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
        "metadata": {"gate": "key_compromise_dual_control_gate"},
    }
    out = evidence_root() / "security" / "key_compromise_dual_control_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"KEY_COMPROMISE_DUAL_CONTROL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
