#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.lib.path_config import evidence_root


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify signed evidence attestation index.")
    parser.add_argument("--strict-key", action="store_true", help="Require GLYPHSER_PROVENANCE_HMAC_KEY.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    index_path = sec / "evidence_attestation_index.json"
    sig_path = sec / "evidence_attestation_index.json.sig"
    findings: list[str] = []

    if not index_path.exists():
        findings.append("missing evidence attestation index")
    if not sig_path.exists():
        findings.append("missing evidence attestation signature")

    items: list[dict[str, Any]] = []
    if not findings:
        sig = sig_path.read_text(encoding="utf-8").strip()
        if not sig:
            findings.append("empty evidence attestation signature")
        elif not verify_file(index_path, sig, key=current_key(strict=args.strict_key)):
            findings.append("evidence attestation signature mismatch")
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid evidence attestation payload")
        else:
            raw_items = payload.get("items", [])
            if not isinstance(raw_items, list):
                findings.append("evidence attestation items must be list")
            else:
                items = [item for item in raw_items if isinstance(item, dict)]

    for item in items:
        seq = item.get("seq", 0)
        if not isinstance(seq, int) or seq <= 0:
            findings.append("invalid attestation sequence number")
            continue
        rel = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        if not rel or not expected:
            findings.append("invalid attestation item")
            continue
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing attested file: {rel}")
            continue
        actual = _sha256_file(path)
        if actual != expected:
            findings.append(f"attested file hash mismatch: {rel}")
    if items:
        seqs = [item.get("seq", 0) for item in items if isinstance(item, dict)]
        if any(not isinstance(v, int) for v in seqs):
            findings.append("attestation sequence values must be integers")
        elif sorted(seqs) != list(range(1, len(seqs) + 1)):
            findings.append("attestation sequence values not strictly monotonic")

    out = sec / "evidence_attestation_gate.json"
    report = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EVIDENCE_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
