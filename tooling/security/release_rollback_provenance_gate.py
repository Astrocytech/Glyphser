#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def _load(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    deploy = evidence_root() / "deploy" / "latest.json"
    rollback = evidence_root() / "deploy" / "rollback.json"
    checklist = ROOT / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    statuses = {
        "deploy": _status(deploy),
        "rollback": _status(rollback),
        "provenance_signature": _status(sec / "provenance_signature.json"),
        "policy_signature": _status(sec / "policy_signature.json"),
        "emergency_lockdown": _status(sec / "emergency_lockdown_gate.json"),
        "security_schema_compatibility_policy": _status(sec / "security_schema_compatibility_policy_gate.json"),
        "conformance_security_coupling": _status(sec / "conformance_security_coupling.json"),
    }
    findings = [f"{k}_not_pass" for k, v in statuses.items() if v != "PASS"]
    deploy_payload = _load(deploy)
    rollback_payload = _load(rollback)
    deploy_policy_digest = str(deploy_payload.get("policy_digest", "")).strip().lower()
    rollback_policy_digest = str(rollback_payload.get("policy_digest", "")).strip().lower()
    rollback_previously_attested = bool(rollback_payload.get("previously_attested", False))
    if not deploy_policy_digest:
        findings.append("missing_deploy_policy_digest")
    elif not DIGEST_RE.fullmatch(deploy_policy_digest):
        findings.append("invalid_deploy_policy_digest")
    if not rollback_policy_digest:
        findings.append("missing_rollback_policy_digest")
    elif not DIGEST_RE.fullmatch(rollback_policy_digest):
        findings.append("invalid_rollback_policy_digest")
    if deploy_policy_digest and rollback_policy_digest and deploy_policy_digest != rollback_policy_digest:
        findings.append("rollback_policy_digest_mismatch")
    if not rollback_previously_attested:
        findings.append("rollback_not_previously_attested")
    required_artifacts = [
        sec / "sbom.json",
        sec / "build_provenance.json",
        sec / "slsa_provenance_v1.json",
        sec / "security_verification_summary.json",
    ]
    missing_artifacts = [str(path.relative_to(ROOT)).replace("\\", "/") for path in required_artifacts if not path.exists()]
    findings.extend(f"missing_rollback_artifact:{rel}" for rel in missing_artifacts)
    if not checklist.exists():
        findings.append("missing_emergency_lockdown_rollback_checklist")
    else:
        text = checklist.read_text(encoding="utf-8", errors="ignore")
        if "rollback attestation verification gate" not in text.lower():
            findings.append("rollback_checklist_missing_attestation_step")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            **statuses,
            "deploy_policy_digest": deploy_policy_digest,
            "rollback_policy_digest": rollback_policy_digest,
            "rollback_previously_attested": rollback_previously_attested,
            "missing_artifacts": missing_artifacts,
            "checklist_path": str(checklist.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "release_rollback_provenance_gate"},
    }
    out = sec / "release_rollback_provenance_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_ROLLBACK_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
