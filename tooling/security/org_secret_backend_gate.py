#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main() -> int:
    policy_path = ROOT / "governance" / "security" / "org_secret_backend_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid org secret backend policy")

    required_backend = str(policy.get("required_backend_type", "")).strip()
    required_mode = str(policy.get("required_credential_mode", "")).strip()
    max_ttl = int(policy.get("max_credential_ttl_hours", 24))
    snapshot_rel = str(policy.get("snapshot_path", "")).strip()
    required_secrets = policy.get("required_secrets", [])
    if not isinstance(required_secrets, list) or not all(isinstance(x, str) and x for x in required_secrets):
        raise ValueError("required_secrets must be list[str]")
    if not snapshot_rel:
        raise ValueError("missing snapshot_path")
    snapshot_path = ROOT / snapshot_rel
    findings: list[str] = []
    if not snapshot_path.exists():
        findings.append(f"missing snapshot: {snapshot_rel}")
        snap: dict[str, Any] = {}
    else:
        snap = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if str(snap.get("backend_type", "")).strip() != required_backend:
        findings.append("backend type mismatch")
    if str(snap.get("credential_mode", "")).strip() != required_mode:
        findings.append("credential mode mismatch")
    ttl = snap.get("credential_ttl_hours")
    if not isinstance(ttl, int) or ttl <= 0 or ttl > max_ttl:
        findings.append("credential ttl exceeds policy")
    managed = snap.get("managed_secrets", [])
    if not isinstance(managed, list):
        managed = []
    missing = sorted([name for name in required_secrets if name not in managed])
    if missing:
        findings.append(f"missing managed secrets: {', '.join(missing)}")

    payload: dict[str, Any] = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_secret_count": len(required_secrets),
            "missing_required_secret_count": len(missing),
            "max_credential_ttl_hours": max_ttl,
        },
        "metadata": {"gate": "org_secret_backend_gate"},
    }
    out = evidence_root() / "security" / "org_secret_backend.json"
    write_json_report(out, payload)
    print(f"ORG_SECRET_BACKEND_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
