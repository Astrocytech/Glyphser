#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


INDEX = "evidence_chain_of_custody.json"
SIG = "evidence_chain_of_custody.json.sig"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_index(strict_key: bool) -> Path:
    ev = evidence_root()
    sec = ev / "security"
    sec.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p
        for p in ev.rglob("*")
        if p.is_file() and p.name not in {INDEX, SIG} and not p.name.endswith(".sig")
    )

    rows: list[dict[str, Any]] = []
    prev = ""
    for ix, path in enumerate(files, start=1):
        digest = _sha256(path)
        row_payload = f"{ix}:{_relative(path)}:{digest}:{prev}"
        chain_hash = hashlib.sha256(row_payload.encode("utf-8")).hexdigest()
        rows.append(
            {
                "seq": ix,
                "path": _relative(path),
                "sha256": digest,
                "prev_chain_hash": prev,
                "chain_hash": chain_hash,
            }
        )
        prev = chain_hash

    payload = {
        "status": "PASS",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "count": len(rows),
        "items": rows,
        "tip_chain_hash": prev,
    }
    index_path = sec / INDEX
    index_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sig_path = sec / SIG
    sig_path.write_text(sign_file(index_path, key=current_key(strict=strict_key)) + "\n", encoding="utf-8")
    return index_path


def verify_index(strict_key: bool) -> dict[str, Any]:
    ev = evidence_root()
    sec = ev / "security"
    index_path = sec / INDEX
    sig_path = sec / SIG
    findings: list[str] = []

    if not index_path.exists():
        findings.append("missing_chain_of_custody_index")
    if not sig_path.exists():
        findings.append("missing_chain_of_custody_signature")
    if findings:
        return {"status": "FAIL", "findings": findings}

    sig = sig_path.read_text(encoding="utf-8").strip()
    if not sig:
        findings.append("empty_chain_of_custody_signature")
    elif not verify_file(index_path, sig, key=current_key(strict=strict_key)):
        findings.append("chain_of_custody_signature_mismatch")

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    rows = payload.get("items", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        findings.append("invalid_chain_of_custody_items")
        rows = []

    prev = ""
    for ix, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            findings.append("invalid_chain_row")
            continue
        seq = row.get("seq")
        rel = str(row.get("path", "")).strip()
        expected_digest = str(row.get("sha256", "")).strip().lower()
        prev_hash = str(row.get("prev_chain_hash", ""))
        chain_hash = str(row.get("chain_hash", ""))
        if seq != ix:
            findings.append("non_monotonic_sequence")
        if prev_hash != prev:
            findings.append("prev_chain_hash_mismatch")
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_attested_file:{rel}")
            continue
        actual_digest = _sha256(path)
        if actual_digest != expected_digest:
            findings.append(f"digest_mismatch:{rel}")
        row_payload = f"{ix}:{rel}:{expected_digest}:{prev_hash}"
        actual_chain_hash = hashlib.sha256(row_payload.encode("utf-8")).hexdigest()
        if chain_hash != actual_chain_hash:
            findings.append(f"chain_hash_mismatch:{rel}")
        prev = chain_hash

    return {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"items": len(rows), "tip_chain_hash": prev},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build/verify evidence chain-of-custody index.")
    parser.add_argument("--strict-key", action="store_true", help="Require explicit signing key env.")
    parser.add_argument("--verify", action="store_true", help="Verify existing chain-of-custody index.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    if args.verify:
        report = verify_index(strict_key=args.strict_key)
        out = sec / "evidence_chain_of_custody_gate.json"
    else:
        index_path = build_index(strict_key=args.strict_key)
        report = {"status": "PASS", "findings": [], "summary": {"index": _relative(index_path)}}
        out = sec / "evidence_chain_of_custody_build.json"

    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EVIDENCE_CHAIN_OF_CUSTODY: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
