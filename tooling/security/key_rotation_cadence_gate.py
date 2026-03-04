#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import bootstrap_key, current_key, verify_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report


def _verify_rotation_signature(path: Path, sig: str) -> bool:
    if verify_file(path, sig, key=current_key(strict=False)):
        return True
    return verify_file(path, sig, key=bootstrap_key())


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy_path = ROOT / "governance" / "security" / "key_management_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid key management policy")

    max_age_days = int(policy.get("maximum_rotation_age_days", 90))
    max_rollover_days = int(policy.get("maximum_rollover_window_days", 14))
    rotation_rel = str(policy.get("rotation_record_path", "governance/security/key_rotation_record.json"))
    require_signed = bool(policy.get("require_signed_rotation_record", True))
    record_path = ROOT / rotation_rel
    findings: list[str] = []
    summary: dict[str, object] = {
        "rotation_record_path": rotation_rel,
        "maximum_rotation_age_days": max_age_days,
        "maximum_rollover_window_days": max_rollover_days,
    }

    if not record_path.exists():
        findings.append("missing_rotation_record")
    else:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_rotation_record")
        else:
            rotated = str(payload.get("rotated_at_utc", "")).strip()
            key_id = str(payload.get("key_id", "")).strip()
            previous_key_id = str(payload.get("previous_key_id", "")).strip()
            previous_key_accept_until = str(payload.get("previous_key_accept_until_utc", "")).strip()
            summary["key_id"] = key_id
            if not key_id:
                findings.append("rotation_record_missing_key_id")
            if not rotated:
                findings.append("rotation_record_missing_rotated_at")
            else:
                try:
                    when = datetime.fromisoformat(rotated.replace("Z", "+00:00"))
                    if when.tzinfo is None:
                        when = when.replace(tzinfo=UTC)
                    age_days = (datetime.now(UTC) - when.astimezone(UTC)).days
                    summary["rotation_age_days"] = age_days
                    if age_days > max_age_days:
                        findings.append("rotation_record_too_old")

                    if previous_key_id:
                        summary["previous_key_id"] = previous_key_id
                        if not previous_key_accept_until:
                            findings.append("missing_previous_key_accept_until")
                        else:
                            try:
                                accept_until = datetime.fromisoformat(previous_key_accept_until.replace("Z", "+00:00"))
                                if accept_until.tzinfo is None:
                                    accept_until = accept_until.replace(tzinfo=UTC)
                                accept_until = accept_until.astimezone(UTC)
                                now = datetime.now(UTC)
                                if now > accept_until:
                                    findings.append("previous_key_acceptance_window_expired")
                                rollover_days = max((accept_until - when.astimezone(UTC)).days, 0)
                                summary["rollover_window_days"] = rollover_days
                                if rollover_days > max_rollover_days:
                                    findings.append("previous_key_acceptance_window_too_long")
                            except ValueError:
                                findings.append("invalid_previous_key_accept_until_timestamp")
                except ValueError:
                    findings.append("rotation_record_invalid_timestamp")

        if require_signed:
            sig_path = record_path.with_suffix(record_path.suffix + ".sig")
            if not sig_path.exists():
                findings.append("missing_rotation_record_signature")
            else:
                sig = sig_path.read_text(encoding="utf-8").strip()
                if not sig:
                    findings.append("empty_rotation_record_signature")
                elif not _verify_rotation_signature(record_path, sig):
                    findings.append("invalid_rotation_record_signature")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "key_rotation_cadence_gate"},
    }
    out = evidence_root() / "security" / "key_rotation_cadence_gate.json"
    write_json_report(out, report)
    print(f"KEY_ROTATION_CADENCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
