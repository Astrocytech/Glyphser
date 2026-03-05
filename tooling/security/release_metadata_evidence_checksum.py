#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _package_entries(sec: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(sec.glob("*.json")):
        if path.name in {
            "release_metadata.json",
            "release_metadata_evidence_checksum_gate.json",
        }:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        entries.append({"path": rel, "sha256": f"sha256:{_sha256(path)}"})
    return entries


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    entries = _package_entries(sec)
    checksum = hashlib.sha256(_canonical(entries).encode("utf-8")).hexdigest()

    metadata_path = sec / "release_metadata.json"
    if metadata_path.exists():
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata = payload if isinstance(payload, dict) else {}
    else:
        metadata = {}

    metadata["evidence_package_checksum"] = f"sha256:{checksum}"
    metadata["evidence_package_file_count"] = len(entries)
    metadata["evidence_package_entries"] = entries
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reloaded = json.loads(metadata_path.read_text(encoding="utf-8"))
    embedded = str((reloaded.get("evidence_package_checksum", "") if isinstance(reloaded, dict) else "")).strip()

    findings: list[str] = []
    if embedded != f"sha256:{checksum}":
        findings.append("embedded_evidence_checksum_mismatch")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "release_metadata_path": str(metadata_path.relative_to(ROOT)).replace("\\", "/"),
            "evidence_package_checksum": f"sha256:{checksum}",
            "evidence_package_file_count": len(entries),
        },
        "metadata": {"gate": "release_metadata_evidence_checksum"},
    }
    out = sec / "release_metadata_evidence_checksum_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_METADATA_EVIDENCE_CHECKSUM: {report['status']}")
    print(f"Metadata: {metadata_path}")
    print(f"Gate: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
