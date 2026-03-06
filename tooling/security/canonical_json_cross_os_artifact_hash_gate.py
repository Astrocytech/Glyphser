#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

TARGET_FILENAMES = (
    "security_gate_parity_snapshot.json",
    "signed_json_hash_equivalence_gate.json",
    "security_event_schema_gate.json",
    "runtime_api_scope_matrix_gate.json",
)


def _canonical_hash(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _find_single(base: Path, filename: str) -> Path | None:
    matches = sorted(base.rglob(filename))
    if not matches:
        return None
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare canonical JSON hashes across Linux/macOS artifact snapshots.")
    parser.add_argument("--left-dir", required=True, help="Artifact root for first OS (e.g., Linux).")
    parser.add_argument("--right-dir", required=True, help="Artifact root for second OS (e.g., macOS).")
    args = parser.parse_args([] if argv is None else argv)

    left_dir = Path(args.left_dir)
    right_dir = Path(args.right_dir)
    findings: list[str] = []
    comparisons: list[dict[str, Any]] = []

    for filename in TARGET_FILENAMES:
        left = _find_single(left_dir, filename)
        right = _find_single(right_dir, filename)
        if left is None:
            findings.append(f"missing_left_artifact:{filename}")
            continue
        if right is None:
            findings.append(f"missing_right_artifact:{filename}")
            continue
        try:
            left_hash = _canonical_hash(left)
            right_hash = _canonical_hash(right)
        except Exception:
            findings.append(f"invalid_json_artifact:{filename}")
            continue
        comparisons.append(
            {
                "filename": filename,
                "left_path": str(left),
                "right_path": str(right),
                "left_hash": left_hash,
                "right_hash": right_hash,
                "match": left_hash == right_hash,
            }
        )
        if left_hash != right_hash:
            findings.append(f"canonical_json_hash_mismatch:{filename}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "left_dir": str(left_dir),
            "right_dir": str(right_dir),
            "target_filenames": list(TARGET_FILENAMES),
            "compared_artifacts": len(comparisons),
        },
        "comparisons": comparisons,
        "metadata": {"gate": "canonical_json_cross_os_artifact_hash_gate"},
    }
    out = evidence_root() / "security" / "canonical_json_cross_os_artifact_hash_gate.json"
    write_json_report(out, report)
    print(f"CANONICAL_JSON_CROSS_OS_ARTIFACT_HASH_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
