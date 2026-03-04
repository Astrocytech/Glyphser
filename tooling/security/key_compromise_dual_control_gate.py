#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
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

    toggle = payload.get("toggle_approval", {})
    if not isinstance(toggle, dict):
        toggle = {}
    ticket_id = str(toggle.get("ticket_id", "")).strip()
    approved_at = str(toggle.get("approved_at_utc", "")).strip()
    if not ticket_id:
        findings.append("missing_toggle_approval_ticket")
    if not approved_at:
        findings.append("missing_toggle_approval_timestamp")
    else:
        try:
            parsed = datetime.fromisoformat(approved_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            if parsed.astimezone(UTC) > datetime.now(UTC):
                findings.append("invalid_toggle_approval_timestamp_future")
        except ValueError:
            findings.append("invalid_toggle_approval_timestamp")

    if payload.get("emergency_disable_exercised") is True:
        disable_at = str(payload.get("disable_executed_at_utc", "")).strip()
        restore_at = str(payload.get("restored_at_utc", "")).strip()
        if not disable_at:
            findings.append("missing_disable_executed_at")
        if not restore_at:
            findings.append("missing_restored_at")
        if payload.get("restoration_verified") is not True:
            findings.append("restoration_not_verified")
        if disable_at and restore_at:
            try:
                dt_disable = datetime.fromisoformat(disable_at.replace("Z", "+00:00"))
                dt_restore = datetime.fromisoformat(restore_at.replace("Z", "+00:00"))
                if dt_disable.tzinfo is None:
                    dt_disable = dt_disable.replace(tzinfo=UTC)
                if dt_restore.tzinfo is None:
                    dt_restore = dt_restore.replace(tzinfo=UTC)
                if dt_restore.astimezone(UTC) <= dt_disable.astimezone(UTC):
                    findings.append("invalid_restore_timeline")
            except ValueError:
                findings.append("invalid_disable_or_restore_timestamp")

    sig = drill_path.with_suffix(drill_path.suffix + ".sig")
    if drill_path.exists() and not sig.exists():
        sig.write_text(sign_file(drill_path, key=current_key(strict=False)) + "\n", encoding="utf-8")
    if drill_path.exists() and sig.exists():
        if not verify_file(drill_path, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False)):
            findings.append("drill_signature_invalid")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"drill_path": str(drill_path.relative_to(ROOT)).replace("\\", "/")},
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
