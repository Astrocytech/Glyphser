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
verify_file = artifact_signing.verify_file
current_key = artifact_signing.current_key
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def _valid_meta(meta: dict[str, Any]) -> bool:
    required = {"title", "owner", "version", "last_reviewed_utc"}
    return required.issubset(meta.keys()) and all(isinstance(meta[k], str) and meta[k].strip() for k in required)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    manifest_path = ROOT / "governance" / "security" / "governance_markdown_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = manifest.get("documents", []) if isinstance(manifest, dict) else []
    findings: list[str] = []

    for entry in docs:
        if not isinstance(entry, dict):
            findings.append("invalid_manifest_entry")
            continue
        doc = ROOT / str(entry.get("path", ""))
        meta_path = ROOT / str(entry.get("metadata_path", ""))
        sig_path = ROOT / str(entry.get("signature_path", ""))
        if not doc.exists():
            findings.append(f"missing_doc:{doc}")
            continue
        if not meta_path.exists():
            findings.append(f"missing_metadata:{meta_path}")
            continue
        if not sig_path.exists():
            findings.append(f"missing_metadata_signature:{sig_path}")
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_metadata_json:{meta_path}")
            continue
        if not isinstance(meta, dict) or not _valid_meta(meta):
            findings.append(f"invalid_metadata_schema:{meta_path}")
        sig = sig_path.read_text(encoding="utf-8").strip()
        if not sig or not verify_file(meta_path, sig, key=current_key(strict=False)):
            findings.append(f"metadata_signature_mismatch:{meta_path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"documents": len(docs)},
        "metadata": {"gate": "governance_markdown_gate"},
    }
    out = evidence_root() / "security" / "governance_markdown_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GOVERNANCE_MARKDOWN_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
