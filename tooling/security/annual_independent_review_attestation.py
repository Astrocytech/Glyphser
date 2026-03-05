#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

CHECKLIST = ROOT / "governance" / "security" / "ANNUAL_INDEPENDENT_REVIEW_CHECKLIST.md"
POLICY = ROOT / "product" / "handbook" / "policies" / "ANNUAL_SECURITY_REVIEW_POLICY.md"
REQUIRED_CHECKLIST_SNIPPETS = [
    "reviewer independence",
    "scope",
    "findings",
    "signed annual independent review attestation",
]
REQUIRED_EVIDENCE = [
    "security/formal_security_review_artifact.json",
    "security/security_super_gate.json",
    "security/security_verification_summary.json",
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate annual independent review attestation.")
    parser.add_argument("--strict-key", action="store_true", help="Require explicit signing key env.")
    args = parser.parse_args([] if argv is None else argv)

    findings: list[str] = []
    if not CHECKLIST.exists():
        findings.append("missing_annual_independent_review_checklist")
        checklist_text = ""
    else:
        checklist_text = CHECKLIST.read_text(encoding="utf-8").lower()
        for snippet in REQUIRED_CHECKLIST_SNIPPETS:
            if snippet not in checklist_text:
                findings.append(f"missing_checklist_requirement:{snippet}")
    if not POLICY.exists():
        findings.append("missing_annual_security_review_policy")

    reviewer = str(os.environ.get("GLYPHSER_INDEPENDENT_REVIEWER", "")).strip()
    approver = str(os.environ.get("GLYPHSER_INDEPENDENT_REVIEW_APPROVER", "")).strip()
    if not reviewer:
        findings.append("missing_env:GLYPHSER_INDEPENDENT_REVIEWER")
    if not approver:
        findings.append("missing_env:GLYPHSER_INDEPENDENT_REVIEW_APPROVER")

    ev = evidence_root()
    evidence_summary: list[dict[str, str]] = []
    for rel in REQUIRED_EVIDENCE:
        path = ev / rel
        relpath = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append(f"missing_required_evidence:{relpath}")
            continue
        try:
            payload = _load_json(path)
        except Exception:
            findings.append(f"invalid_required_evidence:{relpath}")
            continue
        evidence_summary.append(
            {
                "path": relpath,
                "status": str(payload.get("status", "UNKNOWN")).upper(),
                "sha256": f"sha256:{_sha256(path)}",
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "reviewer": reviewer,
            "approver": approver,
            "checklist_path": str(CHECKLIST.relative_to(ROOT)).replace("\\", "/"),
            "reviewed_evidence_count": len(evidence_summary),
            "required_evidence_count": len(REQUIRED_EVIDENCE),
        },
        "reviewed_evidence": evidence_summary,
        "metadata": {"gate": "annual_independent_review_attestation"},
    }
    out = ev / "security" / "annual_independent_review_attestation.json"
    write_json_report(out, report)
    sig = sign_file(out, key=current_key(strict=args.strict_key))
    out.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")
    print(f"ANNUAL_INDEPENDENT_REVIEW_ATTESTATION: {report['status']}")
    print(f"Report: {out}")
    print(f"Signature: {out.with_suffix('.json.sig')}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
