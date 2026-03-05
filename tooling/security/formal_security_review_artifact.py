#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

REQUIRED_REVIEW_ARTIFACTS = [
    "security/security_super_gate.json",
    "security/security_verification_summary.json",
    "security/security_posture_executive_summary.json",
    "security/security_state_transition_invariants_gate.json",
]


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate signed formal security review artifact.")
    parser.add_argument("--strict-key", action="store_true", help="Require explicit signing key env.")
    args = parser.parse_args([] if argv is None else argv)

    ev = evidence_root()
    findings: list[str] = []
    reviewed: list[dict[str, str]] = []
    for rel in REQUIRED_REVIEW_ARTIFACTS:
        path = ev / rel
        relpath = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append(f"missing_review_artifact:{relpath}")
            continue
        try:
            payload = _load(path)
        except Exception:
            findings.append(f"invalid_review_artifact:{relpath}")
            continue
        reviewed.append(
            {
                "path": relpath,
                "status": str(payload.get("status", "UNKNOWN")).upper(),
                "sha256": f"sha256:{_sha256(path)}",
            }
        )

    owner = str(os.environ.get("GLYPHSER_SECURITY_OWNER", "")).strip()
    if not owner:
        findings.append("missing_env:GLYPHSER_SECURITY_OWNER")

    generated_at = datetime.now(UTC).isoformat()
    review_payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "security_owner": owner,
            "generated_at": generated_at,
            "reviewed_artifact_count": len(reviewed),
            "required_artifact_count": len(REQUIRED_REVIEW_ARTIFACTS),
        },
        "reviewed_artifacts": reviewed,
        "metadata": {"gate": "formal_security_review_artifact"},
    }
    out = ev / "security" / "formal_security_review_artifact.json"
    write_json_report(out, review_payload)
    sig = sign_file(out, key=current_key(strict=args.strict_key))
    out.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")
    print(f"FORMAL_SECURITY_REVIEW_ARTIFACT: {review_payload['status']}")
    print(f"Report: {out}")
    print(f"Signature: {out.with_suffix('.json.sig')}")
    return 0 if review_payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
