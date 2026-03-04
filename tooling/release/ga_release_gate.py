#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "ga"
sys.path.insert(0, str(ROOT))


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status_ok(path: Path) -> bool:
    return path.exists() and _load_json(path).get("status") == "PASS"


def main() -> int:
    from tooling.lib.path_config import (
        bundles_root,
        conformance_reports_root,
        evidence_root,
        first_existing,
        rel,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    required_docs = [
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_SUPPORT_MATRIX.md"),
                rel("docs", "product", "GA_SUPPORT_MATRIX.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "guides", "GA_MIGRATION_GUIDE.md"),
                rel("docs", "product", "GA_MIGRATION_GUIDE.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_SUPPORT_LIFECYCLE.md"),
                rel("docs", "product", "GA_SUPPORT_LIFECYCLE.md"),
            ]
        ),
        first_existing(
            [
                rel(
                    "product",
                    "handbook",
                    "policies",
                    "GA_STATUS_INCIDENT_COMMUNICATION.md",
                ),
                rel("docs", "product", "GA_STATUS_INCIDENT_COMMUNICATION.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_RELEASE_TRAIN_POLICY.md"),
                rel("docs", "product", "GA_RELEASE_TRAIN_POLICY.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_CONTRACTUAL_SUPPORT_SLA.md"),
                rel("docs", "product", "GA_CONTRACTUAL_SUPPORT_SLA.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_GO_NO_GO_CHECKLIST.md"),
                rel("docs", "product", "GA_GO_NO_GO_CHECKLIST.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "COMPLIANCE_EVIDENCE_INDEX.md"),
                rel("docs", "product", "COMPLIANCE_EVIDENCE_INDEX.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "DEPENDENCY_LICENSE_REVIEW.md"),
                rel("docs", "product", "DEPENDENCY_LICENSE_REVIEW.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_COMPATIBILITY_GUARANTEES.md"),
                rel("docs", "product", "GA_COMPATIBILITY_GUARANTEES.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "POST_GA_GOVERNANCE.md"),
                rel("docs", "product", "POST_GA_GOVERNANCE.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "reports", "ACCESSIBILITY_REVIEW.md"),
                rel("docs", "product", "ACCESSIBILITY_REVIEW.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "SUPPLY_CHAIN_TRUST_POLICY.md"),
                rel("docs", "product", "SUPPLY_CHAIN_TRUST_POLICY.md"),
            ]
        ),
        first_existing(
            [
                rel(
                    "product",
                    "handbook",
                    "policies",
                    "PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md",
                ),
                rel("docs", "product", "PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "DOCS_VERSIONING_POLICY.md"),
                rel("docs", "product", "DOCS_VERSIONING_POLICY.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "CHANGE_COMMUNICATION_SLA.md"),
                rel("docs", "product", "CHANGE_COMMUNICATION_SLA.md"),
            ]
        ),
        first_existing(
            [
                rel(
                    "product",
                    "handbook",
                    "policies",
                    "ANNUAL_SECURITY_REVIEW_POLICY.md",
                ),
                rel("docs", "product", "ANNUAL_SECURITY_REVIEW_POLICY.md"),
            ]
        ),
        first_existing(
            [
                rel("product", "handbook", "policies", "GA_SIGNOFF.md"),
                rel("docs", "product", "GA_SIGNOFF.md"),
            ]
        ),
        first_existing(
            [
                rel(
                    "product",
                    "handbook",
                    "policies",
                    "GA_SUPPORT_OPERATIONS_READINESS.md",
                ),
                rel("docs", "product", "GA_SUPPORT_OPERATIONS_READINESS.md"),
            ]
        ),
    ]
    required_artifacts = [
        first_existing(
            [
                rel("distribution", "release", "CHECKSUMS_v0.1.0.sha256"),
                rel("docs", "release", "CHECKSUMS_v0.1.0.sha256"),
            ]
        ),
        first_existing(
            [
                rel("distribution", "release", "CHECKSUMS_v0.1.0.sha256.asc"),
                rel("docs", "release", "CHECKSUMS_v0.1.0.sha256.asc"),
            ]
        ),
        first_existing(
            [
                rel("distribution", "release", "RELEASE_PUBKEY.asc"),
                rel("docs", "release", "RELEASE_PUBKEY.asc"),
            ]
        ),
        first_existing(
            [
                rel("distribution", "release", "RELEASE_NOTES_v0.1.0.md"),
                rel("RELEASE_NOTES_v0.1.0.md"),
            ]
        ),
        conformance_reports_root() / "latest.json",
        bundles_root() / "hello-core-bundle.tar.gz",
        bundles_root() / "hello-core-bundle.sha256",
    ]
    missing_docs = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required_docs if not p.exists()]
    missing_artifacts = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required_artifacts if not p.exists()]

    gate_checks = {
        "security": _status_ok(evidence_root() / "security" / "latest.json"),
        "recovery": _status_ok(evidence_root() / "recovery" / "latest.json"),
        "deploy": _status_ok(evidence_root() / "deploy" / "latest.json"),
        "observability": _status_ok(evidence_root() / "observability" / "latest.json"),
        "external_validation": _status_ok(evidence_root() / "validation" / "latest.json"),
        "conformance": _status_ok(conformance_reports_root() / "latest.json"),
    }
    signatures = {
        "checksum_signed": first_existing(
            [
                rel("distribution", "release", "CHECKSUMS_v0.1.0.sha256.asc"),
                rel("docs", "release", "CHECKSUMS_v0.1.0.sha256.asc"),
            ]
        ).exists(),
        "pubkey_present": first_existing(
            [
                rel("distribution", "release", "RELEASE_PUBKEY.asc"),
                rel("docs", "release", "RELEASE_PUBKEY.asc"),
            ]
        ).exists(),
    }

    bundle_path = bundles_root() / "hello-core-bundle.tar.gz"
    conformance_report_path = conformance_reports_root() / "latest.json"
    checksums_path = first_existing(
        [
            rel("distribution", "release", "CHECKSUMS_v0.1.0.sha256"),
            rel("docs", "release", "CHECKSUMS_v0.1.0.sha256"),
        ]
    )

    rc_report = {
        "status": "PASS",
        "bundle_hash": _sha256(bundle_path) if bundle_path.exists() else "",
        "conformance_report_hash": _sha256(conformance_report_path) if conformance_report_path.exists() else "",
        "checksums_file_hash": _sha256(checksums_path) if checksums_path.exists() else "",
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
        "release_candidate_report": "evidence/ga/release_candidate_verification.json",
    }
    (OUT / "latest.json").write_text(json.dumps(latest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if overall:
        print("GA_RELEASE_GATE: PASS")
        return 0
    print("GA_RELEASE_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
