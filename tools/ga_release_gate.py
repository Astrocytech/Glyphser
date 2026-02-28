#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "ga"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status_ok(path: Path) -> bool:
    return path.exists() and _load_json(path).get("status") == "PASS"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    required_docs = [
        ROOT / "docs" / "product" / "GA_SUPPORT_MATRIX.md",
        ROOT / "docs" / "product" / "GA_MIGRATION_GUIDE.md",
        ROOT / "docs" / "product" / "GA_SUPPORT_LIFECYCLE.md",
        ROOT / "docs" / "product" / "GA_STATUS_INCIDENT_COMMUNICATION.md",
        ROOT / "docs" / "product" / "GA_RELEASE_TRAIN_POLICY.md",
        ROOT / "docs" / "product" / "GA_CONTRACTUAL_SUPPORT_SLA.md",
        ROOT / "docs" / "product" / "GA_GO_NO_GO_CHECKLIST.md",
        ROOT / "docs" / "product" / "COMPLIANCE_EVIDENCE_INDEX.md",
        ROOT / "docs" / "product" / "DEPENDENCY_LICENSE_REVIEW.md",
        ROOT / "docs" / "product" / "GA_COMPATIBILITY_GUARANTEES.md",
        ROOT / "docs" / "product" / "POST_GA_GOVERNANCE.md",
        ROOT / "docs" / "product" / "ACCESSIBILITY_REVIEW.md",
        ROOT / "docs" / "product" / "SUPPLY_CHAIN_TRUST_POLICY.md",
        ROOT / "docs" / "product" / "PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md",
        ROOT / "docs" / "product" / "DOCS_VERSIONING_POLICY.md",
        ROOT / "docs" / "product" / "CHANGE_COMMUNICATION_SLA.md",
        ROOT / "docs" / "product" / "ANNUAL_SECURITY_REVIEW_POLICY.md",
        ROOT / "docs" / "product" / "GA_SIGNOFF.md",
        ROOT / "docs" / "product" / "GA_SUPPORT_OPERATIONS_READINESS.md",
    ]
    required_artifacts = [
        ROOT / "docs" / "release" / "CHECKSUMS_v0.1.0.sha256",
        ROOT / "docs" / "release" / "CHECKSUMS_v0.1.0.sha256.asc",
        ROOT / "docs" / "release" / "RELEASE_PUBKEY.asc",
        ROOT / "RELEASE_NOTES_v0.1.0.md",
        ROOT / "conformance" / "reports" / "latest.json",
        ROOT / "dist" / "hello-core-bundle.tar.gz",
        ROOT / "dist" / "hello-core-bundle.sha256",
    ]
    missing_docs = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required_docs if not p.exists()]
    missing_artifacts = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required_artifacts if not p.exists()]

    gate_checks = {
        "security": _status_ok(ROOT / "reports" / "security" / "latest.json"),
        "recovery": _status_ok(ROOT / "reports" / "recovery" / "latest.json"),
        "deploy": _status_ok(ROOT / "reports" / "deploy" / "latest.json"),
        "observability": _status_ok(ROOT / "reports" / "observability" / "latest.json"),
        "external_validation": _status_ok(ROOT / "reports" / "validation" / "latest.json"),
        "conformance": _status_ok(ROOT / "conformance" / "reports" / "latest.json"),
    }
    signatures = {
        "checksum_signed": (ROOT / "docs" / "release" / "CHECKSUMS_v0.1.0.sha256.asc").exists(),
        "pubkey_present": (ROOT / "docs" / "release" / "RELEASE_PUBKEY.asc").exists(),
    }

    rc_report = {
        "status": "PASS",
        "bundle_hash": _sha256(ROOT / "dist" / "hello-core-bundle.tar.gz")
        if (ROOT / "dist" / "hello-core-bundle.tar.gz").exists()
        else "",
        "conformance_report_hash": _sha256(ROOT / "conformance" / "reports" / "latest.json")
        if (ROOT / "conformance" / "reports" / "latest.json").exists()
        else "",
        "checksums_file_hash": _sha256(ROOT / "docs" / "release" / "CHECKSUMS_v0.1.0.sha256")
        if (ROOT / "docs" / "release" / "CHECKSUMS_v0.1.0.sha256").exists()
        else "",
        "security_gate_status": "PASS" if gate_checks["security"] else "FAIL",
        "recovery_gate_status": "PASS" if gate_checks["recovery"] else "FAIL",
        "deploy_gate_status": "PASS" if gate_checks["deploy"] else "FAIL",
        "observability_gate_status": "PASS" if gate_checks["observability"] else "FAIL",
        "external_validation_status": "PASS" if gate_checks["external_validation"] else "FAIL",
    }

    overall = not missing_docs and not missing_artifacts and all(gate_checks.values()) and all(signatures.values())
    if not overall:
        rc_report["status"] = "FAIL"
    (OUT / "release_candidate_verification.json").write_text(
        json.dumps(rc_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    latest = {
        "status": "PASS" if overall else "FAIL",
        "missing_docs": missing_docs,
        "missing_artifacts": missing_artifacts,
        "gate_checks": gate_checks,
        "signatures": signatures,
        "release_candidate_report": "reports/ga/release_candidate_verification.json",
    }
    (OUT / "latest.json").write_text(json.dumps(latest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if overall:
        print("GA_RELEASE_GATE: PASS")
        return 0
    print("GA_RELEASE_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

