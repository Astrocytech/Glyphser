#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    index_path = ROOT / str(policy.get("archive_integrity_index", "evidence/security/archive_integrity_index.json"))
    targets = [ROOT / rel for rel in policy.get("archive_integrity_targets", []) if isinstance(rel, str)]
    findings: list[str] = []
    hashes: dict[str, str] = {}

    if index_path.exists():
        prev = json.loads(index_path.read_text(encoding="utf-8"))
        prev_hashes = prev.get("hashes", {}) if isinstance(prev, dict) else {}
    else:
        prev_hashes = {}

    for path in targets:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append(f"missing_archive_target:{rel}")
            continue
        digest = _sha(path)
        hashes[rel] = digest
        old = prev_hashes.get(rel) if isinstance(prev_hashes, dict) else None
        if old and old != digest:
            findings.append(f"archive_integrity_mismatch:{rel}")

    index_payload = {"hashes": hashes}
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"targets": list(hashes.keys()), "index": str(index_path.relative_to(ROOT)).replace("\\", "/")},
        "metadata": {"gate": "archive_integrity_revalidation_gate"},
    }
    out = evidence_root() / "security" / "archive_integrity_revalidation_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ARCHIVE_INTEGRITY_REVALIDATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
