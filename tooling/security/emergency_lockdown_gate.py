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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def _parse(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = ROOT / "governance" / "security" / "emergency_lockdown_policy.json"
    sig = policy.with_suffix(policy.suffix + ".sig")
    findings: list[str] = []
    payload = json.loads(policy.read_text(encoding="utf-8")) if policy.exists() else {}
    if not isinstance(payload, dict):
        payload = {}
        findings.append("invalid_lockdown_policy")
    if not sig.exists():
        findings.append("missing_lockdown_policy_signature")
    else:
        s = sig.read_text(encoding="utf-8").strip()
        if not s or not verify_file(policy, s, key=current_key(strict=False)):
            findings.append("lockdown_policy_signature_mismatch")

    enabled = payload.get("lockdown_enabled") is True
    expires = _parse(str(payload.get("expires_at_utc", "")))
    if enabled:
        if not str(payload.get("approved_by", "")).strip():
            findings.append("lockdown_missing_approval")
        if expires is None:
            findings.append("lockdown_missing_or_invalid_expiry")
        elif expires <= datetime.now(UTC):
            findings.append("lockdown_expired")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"lockdown_enabled": enabled, "expires_at_utc": payload.get("expires_at_utc", "")},
        "metadata": {"gate": "emergency_lockdown_gate"},
    }
    out = evidence_root() / "security" / "emergency_lockdown_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EMERGENCY_LOCKDOWN_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
