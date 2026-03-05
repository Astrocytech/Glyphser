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

SIGNED_JSON_ROOT = ROOT / "governance" / "security"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot() -> dict[str, Any]:
    findings: list[str] = []
    hashes: dict[str, dict[str, str]] = {}

    for json_path in sorted(SIGNED_JSON_ROOT.rglob("*.json")):
        sig_path = json_path.with_suffix(json_path.suffix + ".sig")
        if not sig_path.exists():
            continue
        rel = str(json_path.relative_to(ROOT)).replace("\\", "/")
        try:
            hashes[rel] = {
                "json_sha256": _sha256(json_path),
                "sig_sha256": _sha256(sig_path),
            }
        except Exception:
            findings.append(f"hash_compute_failed:{rel}")

    return {
        "schema_version": 1,
        "mode": "snapshot",
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "signed_json_artifacts": len(hashes),
            "signed_json_root": str(SIGNED_JSON_ROOT.relative_to(ROOT)).replace("\\", "/"),
        },
        "hashes": hashes,
        "metadata": {"gate": "signed_json_hash_equivalence_gate"},
    }


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid payload at {path}")
    return payload


def _compare(left_path: Path, right_path: Path) -> dict[str, Any]:
    findings: list[str] = []
    left = _load(left_path)
    right = _load(right_path)

    left_hashes = left.get("hashes", {}) if isinstance(left, dict) else {}
    right_hashes = right.get("hashes", {}) if isinstance(right, dict) else {}
    if not isinstance(left_hashes, dict) or not isinstance(right_hashes, dict):
        raise ValueError("snapshot missing hashes map")

    left_keys = set(left_hashes.keys())
    right_keys = set(right_hashes.keys())

    for key in sorted(left_keys - right_keys):
        findings.append(f"missing_on_right:{key}")
    for key in sorted(right_keys - left_keys):
        findings.append(f"missing_on_left:{key}")

    for key in sorted(left_keys & right_keys):
        lval = left_hashes.get(key)
        rval = right_hashes.get(key)
        if not isinstance(lval, dict) or not isinstance(rval, dict):
            findings.append(f"invalid_hash_entry:{key}")
            continue
        if lval.get("json_sha256") != rval.get("json_sha256"):
            findings.append(f"json_hash_mismatch:{key}")
        if lval.get("sig_sha256") != rval.get("sig_sha256"):
            findings.append(f"sig_hash_mismatch:{key}")

    return {
        "schema_version": 1,
        "mode": "compare",
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "left": str(left_path),
            "right": str(right_path),
            "compared_artifacts": len(left_keys & right_keys),
            "left_only": len(left_keys - right_keys),
            "right_only": len(right_keys - left_keys),
        },
        "metadata": {"gate": "signed_json_hash_equivalence_gate"},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Snapshot/compare signed JSON artifact hashes for cross-OS equivalence.")
    parser.add_argument("--left", help="Left snapshot JSON path for compare mode.")
    parser.add_argument("--right", help="Right snapshot JSON path for compare mode.")
    args = parser.parse_args([] if argv is None else argv)

    if bool(args.left) ^ bool(args.right):
        raise ValueError("--left and --right must be provided together")

    if args.left and args.right:
        report = _compare(Path(args.left), Path(args.right))
    else:
        report = _snapshot()

    out = evidence_root() / "security" / "signed_json_hash_equivalence_gate.json"
    write_json_report(out, report)
    print(f"SIGNED_JSON_HASH_EQUIVALENCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
