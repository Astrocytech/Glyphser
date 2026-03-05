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

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "archival_encryption_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_archival_encryption_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    algorithm = str(policy.get("encryption_algorithm", "")).strip()
    kms = str(policy.get("key_management_system", "")).strip()
    owner = str(policy.get("custody_owner", "")).strip()
    backup_owner = str(policy.get("custody_backup_owner", "")).strip()
    rotation_days = int(policy.get("key_rotation_days", 0) or 0)
    max_unencrypted_age_hours = int(policy.get("max_unencrypted_age_hours", 0) or 0)
    evidence_rel = str(policy.get("verification_evidence_path", "")).strip()

    if not algorithm:
        findings.append("missing_encryption_algorithm")
    if not kms:
        findings.append("missing_key_management_system")
    if not owner:
        findings.append("missing_custody_owner")
    if not backup_owner:
        findings.append("missing_custody_backup_owner")
    if rotation_days <= 0:
        findings.append("invalid_key_rotation_days")
    if max_unencrypted_age_hours <= 0:
        findings.append("invalid_max_unencrypted_age_hours")
    if not evidence_rel:
        findings.append("missing_verification_evidence_path")

    evidence_payload: dict[str, Any] = {}
    evidence_path = ROOT / evidence_rel if evidence_rel else Path("")
    if evidence_rel:
        if not evidence_path.exists():
            findings.append("missing_archival_encryption_verification_evidence")
        else:
            evidence_payload = _load_json(evidence_path)
            if str(evidence_payload.get("status", "")).upper() not in {"PASS", "VERIFIED"}:
                findings.append("archival_encryption_evidence_not_verified")
            if not str(evidence_payload.get("verified_at_utc", "")).strip():
                findings.append("missing_archival_encryption_verified_at_utc")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
            "encryption_algorithm": algorithm,
            "key_management_system": kms,
            "custody_owner": owner,
            "custody_backup_owner": backup_owner,
            "key_rotation_days": rotation_days,
            "max_unencrypted_age_hours": max_unencrypted_age_hours,
            "verification_evidence_path": evidence_rel,
            "evidence_verified": str(evidence_payload.get("status", "")).upper() in {"PASS", "VERIFIED"},
        },
        "metadata": {"gate": "archival_encryption_verification_gate"},
    }

    out = evidence_root() / "security" / "archival_encryption_verification_gate.json"
    write_json_report(out, report)
    print(f"ARCHIVAL_ENCRYPTION_VERIFICATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
