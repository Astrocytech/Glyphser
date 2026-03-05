#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence_bundle_digest(sec: Path) -> str:
    super_gate = sec / "security_super_gate.json"
    if super_gate.exists():
        return f"sha256:{_sha256(super_gate)}"
    retention = sec / "long_term_retention_manifest.json"
    if retention.exists():
        payload = json.loads(retention.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            digest = str(((payload.get("summary") or {}) if isinstance(payload.get("summary"), dict) else {}).get("immutable_manifest_digest", "")).strip()
            if digest:
                return digest
    return ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    run_id = os.environ.get("GITHUB_RUN_ID", "").strip() or os.environ.get("GLYPHSER_RUN_ID", "").strip()
    approvers = [x.strip() for x in os.environ.get("GLYPHSER_DEPLOY_APPROVERS", "").split(",") if x.strip()]
    if not run_id:
        findings.append("missing_run_id")
    if not approvers:
        findings.append("missing_approvers")

    digest = _evidence_bundle_digest(sec)
    if not digest:
        findings.append("missing_evidence_bundle_digest")

    record = {
        "status": "PASS" if not findings else "FAIL",
        "run_id": run_id,
        "approvers": approvers,
        "decision": os.environ.get("GLYPHSER_DEPLOY_DECISION", "approved").strip() or "approved",
        "evidence_bundle_digest": digest,
    }
    record_path = sec / "deploy_decision_record.json"
    write_json_report(record_path, record)
    sig_path = record_path.with_suffix(".json.sig")
    sig_path.write_text(sign_file(record_path, key=current_key(strict=False)) + "\n", encoding="utf-8")

    sig = sig_path.read_text(encoding="utf-8").strip()
    if not verify_file(record_path, sig, key=current_key(strict=False)):
        findings.append("deploy_decision_record_signature_invalid")

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"run_id": run_id, "approvers": approvers, "evidence_bundle_digest": digest},
        "metadata": {"gate": "deploy_decision_record"},
    }
    out = sec / "deploy_decision_record_gate.json"
    write_json_report(out, gate)
    print(f"DEPLOY_DECISION_RECORD: {gate['status']}")
    print(f"Record: {record_path}")
    print(f"Gate: {out}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
