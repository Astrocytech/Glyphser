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

from runtime.glyphser.security.artifact_signing import bootstrap_key, current_key, verify_file


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _verify_pair(path: Path, sig: Path) -> bool:
    signature = sig.read_text(encoding="utf-8").strip()
    if not signature:
        return False
    key = current_key(strict=False)
    if verify_file(path, signature, key=key):
        return True
    return verify_file(path, signature, key=bootstrap_key())


def _iter_signature_pairs(bundle: Path) -> tuple[list[tuple[Path, Path]], list[str]]:
    pairs: list[tuple[Path, Path]] = []
    findings: list[str] = []
    for sig in sorted(bundle.glob("*.sig")):
        payload = sig.with_name(sig.name[: -len(".sig")])
        if not payload.exists():
            findings.append(f"missing_signed_payload:{sig.name}")
            continue
        pairs.append((payload, sig))
    return pairs, findings


def _verify_chain_index(path: Path) -> list[str]:
    findings: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", []) if isinstance(payload, dict) else []
    if not isinstance(items, list):
        return ["invalid_chain_items"]
    prev_hash = ""
    seq = 0
    for item in items:
        if not isinstance(item, dict):
            findings.append("invalid_chain_item")
            continue
        seq += 1
        item_seq = item.get("seq")
        if item_seq != seq:
            findings.append("chain_seq_not_monotonic")
        item_prev = str(item.get("previous_hash", ""))
        if item_prev != prev_hash:
            findings.append("chain_previous_hash_mismatch")
        digest = str(item.get("digest", ""))
        record = dict(item)
        record.pop("digest", None)
        expected = hashlib.sha256(_canonical_json(record).encode("utf-8")).hexdigest()
        if digest != expected:
            findings.append("chain_digest_mismatch")
        prev_hash = digest
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline verification of signatures and chain-of-custody artifacts.")
    parser.add_argument("--bundle-dir", default=str(ROOT / "evidence" / "security" / "offline_verify_bundle"))
    args = parser.parse_args([] if argv is None else argv)

    bundle = Path(args.bundle_dir)
    findings: list[str] = []
    checks: dict[str, bool] = {}
    pairs, pair_findings = _iter_signature_pairs(bundle)
    findings.extend(pair_findings)
    for path, sig in pairs:
        ok = _verify_pair(path, sig)
        checks[path.name] = ok
        if not ok:
            findings.append(f"invalid_signature:{path.name}")

    chain = bundle / "evidence_chain_of_custody.json"
    if chain.exists():
        chain_findings = _verify_chain_index(chain)
        findings.extend(chain_findings)

    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {"bundle_dir": str(bundle), "signature_checks": checks, "verified_files": len(checks)},
    }
    report_path = bundle / "offline_verify_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OFFLINE_VERIFY: {status}")
    print(f"Report: {report_path}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
