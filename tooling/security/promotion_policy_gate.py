#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "promotion_policy.json"
OVERRIDE = ROOT / "governance" / "security" / "promotion_override.json"


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def _parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _valid_override(now: datetime) -> tuple[bool, dict[str, Any], str]:
    if not OVERRIDE.exists():
        return False, {}, "override_not_present"
    sig_path = OVERRIDE.with_suffix(".json.sig")
    if not sig_path.exists():
        return False, {}, "override_signature_missing"
    sig = sig_path.read_text(encoding="utf-8").strip()
    if not sig:
        return False, {}, "override_signature_empty"
    key = artifact_signing.current_key(strict=False)
    if not artifact_signing.verify_file(OVERRIDE, sig, key=key):
        return False, {}, "override_signature_invalid"
    payload = json.loads(OVERRIDE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return False, {}, "override_invalid_payload"
    owner = str(payload.get("owner", "")).strip()
    reason = str(payload.get("reason", "")).strip()
    exp_raw = str(payload.get("expires_at_utc", "")).strip()
    expires_at = _parse_ts(exp_raw)
    if not owner:
        return False, payload, "override_missing_owner"
    if not reason:
        return False, payload, "override_missing_reason"
    if expires_at is None:
        return False, payload, "override_invalid_expiry"
    if expires_at <= now:
        return False, payload, "override_expired"
    return True, payload, "override_valid"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid promotion policy")
    required = policy.get("required_reports", [])
    if not isinstance(required, list):
        raise ValueError("invalid promotion policy required_reports")
    required_reports = [str(item).strip() for item in required if isinstance(item, str) and str(item).strip()]

    sec = evidence_root() / "security"
    statuses = {name: _status(sec / name) for name in required_reports}
    hard_fail = [
        f"mandatory_evidence_missing:{name}:{status}"
        for name, status in statuses.items()
        if status in {"MISSING", "INVALID"}
    ]
    soft_fail = [f"required_report_not_pass:{name}:{status}" for name, status in statuses.items() if status not in {"PASS", "MISSING", "INVALID"}]
    findings = list(hard_fail) + list(soft_fail)

    now = datetime.now(UTC)
    override_ok, override_payload, override_reason = _valid_override(now)
    allow_override = bool(policy.get("allow_signed_override", True))
    override_applied = bool(soft_fail) and not hard_fail and allow_override and override_ok
    if override_applied:
        findings = list(hard_fail)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_reports": required_reports,
            "statuses": statuses,
            "hard_failures": hard_fail,
            "soft_failures": soft_fail,
            "allow_signed_override": allow_override,
            "override_applied": override_applied,
            "override_reason": override_reason,
        },
        "metadata": {
            "gate": "promotion_policy_gate",
            "override_owner": str(override_payload.get("owner", "")) if override_applied else "",
        },
    }
    out = sec / "promotion_policy_gate.json"
    write_json_report(out, report)
    print(f"PROMOTION_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
