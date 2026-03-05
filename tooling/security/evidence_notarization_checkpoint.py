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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "evidence" / "security" / "long_term_retention_manifest.json"
RECEIPT = ROOT / "evidence" / "security" / "evidence_notarization_receipt.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not MANIFEST.exists():
        findings.append("missing_long_term_retention_manifest")
        manifest = {}
    else:
        manifest = _load_json(MANIFEST)

    if not RECEIPT.exists():
        findings.append("missing_evidence_notarization_receipt")
        receipt = {}
    else:
        receipt = _load_json(RECEIPT)

    sig_path = RECEIPT.with_suffix(".json.sig")
    if RECEIPT.exists():
        if not sig_path.exists():
            findings.append("missing_evidence_notarization_receipt_signature")
        else:
            sig = sig_path.read_text(encoding="utf-8").strip()
            if not sig:
                findings.append("empty_evidence_notarization_receipt_signature")
            elif not verify_file(RECEIPT, sig, key=current_key(strict=False)):
                findings.append("invalid_evidence_notarization_receipt_signature")

    expected_digest = str(((manifest.get("summary") or {}) if isinstance(manifest.get("summary"), dict) else {}).get("immutable_manifest_digest", "")).strip()
    observed_digest = str(receipt.get("long_term_retention_manifest_digest", "")).strip() if isinstance(receipt, dict) else ""
    if expected_digest and observed_digest and expected_digest != observed_digest:
        findings.append("notarization_receipt_digest_mismatch")
    if RECEIPT.exists() and not observed_digest:
        findings.append("missing_notarized_manifest_digest")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "receipt_path": str(RECEIPT.relative_to(ROOT)).replace("\\", "/"),
            "manifest_digest": expected_digest,
            "receipt_manifest_digest": observed_digest,
        },
        "metadata": {"gate": "evidence_notarization_checkpoint"},
    }
    out = evidence_root() / "security" / "evidence_notarization_checkpoint.json"
    write_json_report(out, report)
    print(f"EVIDENCE_NOTARIZATION_CHECKPOINT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
