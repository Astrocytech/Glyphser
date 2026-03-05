#!/usr/bin/env python3
from __future__ import annotations

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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "evidence" / "security" / "long_term_retention_manifest.json"
CHAIN = ROOT / "evidence" / "security" / "manifest_pointer_meta_chain.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not MANIFEST.exists():
        findings.append("missing_long_term_retention_manifest")
        manifest_sha = ""
    else:
        manifest_sha = f"sha256:{_sha256(MANIFEST)}"

    chain_doc = _load_json(CHAIN) if CHAIN.exists() else {}
    entries = chain_doc.get("entries", []) if isinstance(chain_doc, dict) else []
    if not isinstance(entries, list):
        entries = []
        findings.append("invalid_meta_chain_entries")

    prev_chain_digest = ""
    if entries:
        prev_chain_digest = str(entries[-1].get("chain_digest", "")).strip() if isinstance(entries[-1], dict) else ""

    if manifest_sha:
        newest = entries[-1] if entries and isinstance(entries[-1], dict) else {}
        if str(newest.get("manifest_sha256", "")).strip() != manifest_sha:
            draft = {
                "recorded_at_utc": datetime.now(UTC).isoformat(),
                "manifest_path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
                "manifest_sha256": manifest_sha,
                "previous_chain_digest": prev_chain_digest,
            }
            chain_digest = hashlib.sha256(_canonical(draft).encode("utf-8")).hexdigest()
            draft["chain_digest"] = f"sha256:{chain_digest}"
            entries.append(draft)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "manifest_sha256": manifest_sha,
            "chain_length": len(entries),
            "head_chain_digest": str(entries[-1].get("chain_digest", "")).strip() if entries and isinstance(entries[-1], dict) else "",
        },
        "metadata": {"gate": "manifest_pointer_meta_chain"},
        "entries": entries,
    }

    out = evidence_root() / "security" / "manifest_pointer_meta_chain.json"
    write_json_report(out, report)

    sig_path = out.with_suffix(".json.sig")
    signature = sign_file(out, key=current_key(strict=False))
    sig_path.write_text(signature + "\n", encoding="utf-8")
    if not verify_file(out, signature, key=current_key(strict=False)):
        report["status"] = "FAIL"
        report.setdefault("findings", []).append("manifest_meta_chain_signature_invalid")
        write_json_report(out, report)

    print(f"MANIFEST_POINTER_META_CHAIN: {report['status']}")
    print(f"Report: {out}")
    print(f"Signature: {sig_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
