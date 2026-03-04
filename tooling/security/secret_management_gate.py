#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root


def _parse_utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _age_days(text: str) -> int:
    return int((datetime.now(UTC) - _parse_utc(text)).total_seconds() // 86400)


def main() -> int:
    policy_path = ROOT / "governance" / "security" / "secret_management_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid secret management policy")

    required_backend = str(policy.get("required_backend", "")).strip()
    max_age = int(policy.get("max_secret_rotation_age_days", 90))
    required_secrets = policy.get("required_secrets", [])
    if not isinstance(required_secrets, list) or not all(isinstance(x, str) and x for x in required_secrets):
        raise ValueError("required_secrets must be list[str]")
    audit_rel = str(policy.get("rotation_audit_log", "")).strip()
    if not audit_rel:
        raise ValueError("missing rotation_audit_log")
    audit_path = ROOT / audit_rel
    findings: list[str] = []
    if not audit_path.exists():
        findings.append(f"missing secret rotation audit log: {audit_rel}")
        audit: dict[str, Any] = {}
    else:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    backend = str(audit.get("backend", "")).strip()
    if backend != required_backend:
        findings.append(f"backend mismatch: expected {required_backend}, got {backend or 'empty'}")
    rotated = audit.get("secrets_rotated", [])
    if not isinstance(rotated, list):
        rotated = []
    missing = sorted([name for name in required_secrets if name not in rotated])
    if missing:
        findings.append(f"required secrets missing from rotation log: {', '.join(missing)}")
    last_rotation = str(audit.get("last_rotation_utc", "")).strip()
    if not last_rotation:
        findings.append("missing last_rotation_utc")
    else:
        if _age_days(last_rotation) > max_age:
            findings.append("secret rotation stale")

    payload: dict[str, Any] = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    out = evidence_root() / "security" / "secret_management.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECRET_MANAGEMENT_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
