#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid report payload: {path}")
    return payload


def _coerce_matrix(payload: dict[str, Any]) -> dict[str, dict[str, str]]:
    raw = payload.get("summary", {})
    if not isinstance(raw, dict):
        return {}
    matrix = raw.get("matrix", {})
    if not isinstance(matrix, dict):
        return {}
    out: dict[str, dict[str, str]] = {}
    for key, value in matrix.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        mode = value.get("mode")
        platform = value.get("platform")
        if isinstance(mode, str):
            out[key] = {
                "mode": mode,
                "platform": platform if isinstance(platform, str) else "",
            }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare filesystem permission parity for sensitive outputs.")
    parser.add_argument("--left", required=True, help="Path to first file_permission_matrix_gate report.")
    parser.add_argument("--right", required=True, help="Path to second file_permission_matrix_gate report.")
    parser.add_argument("--left-label", default="left", help="Human-readable label for the left report.")
    parser.add_argument("--right-label", default="right", help="Human-readable label for the right report.")
    args = parser.parse_args([] if argv is None else argv)

    findings: list[str] = []
    left = _load(Path(args.left))
    right = _load(Path(args.right))
    left_hash = str(left.get("parity_hash", "")).strip()
    right_hash = str(right.get("parity_hash", "")).strip()
    left_matrix = _coerce_matrix(left)
    right_matrix = _coerce_matrix(right)

    if not left_hash:
        findings.append(f"missing_parity_hash:{args.left_label}")
    if not right_hash:
        findings.append(f"missing_parity_hash:{args.right_label}")
    if left_hash and right_hash and left_hash != right_hash:
        findings.append(f"parity_hash_mismatch:{args.left_label}:{args.right_label}")
    all_paths = sorted(set(left_matrix) | set(right_matrix))
    parity_details: list[dict[str, str]] = []
    for path in all_paths:
        left_mode = left_matrix.get(path, {}).get("mode", "")
        right_mode = right_matrix.get(path, {}).get("mode", "")
        if not left_mode:
            findings.append(f"missing_sensitive_output:{args.left_label}:{path}")
        if not right_mode:
            findings.append(f"missing_sensitive_output:{args.right_label}:{path}")
        if left_mode and right_mode and left_mode != right_mode:
            findings.append(
                f"mode_mismatch:{path}:{args.left_label}={left_mode}:{args.right_label}={right_mode}"
            )
        parity_details.append(
            {
                "path": path,
                f"{args.left_label}_mode": left_mode or "MISSING",
                f"{args.right_label}_mode": right_mode or "MISSING",
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "left_label": args.left_label,
            "right_label": args.right_label,
            "left_hash": left_hash,
            "right_hash": right_hash,
            "left_report": str(Path(args.left)),
            "right_report": str(Path(args.right)),
            "sensitive_output_count_left": len(left_matrix),
            "sensitive_output_count_right": len(right_matrix),
            "parity_details": parity_details,
        },
        "metadata": {"gate": "filesystem_permission_parity_report"},
    }
    out = evidence_root() / "security" / "filesystem_permission_parity_report.json"
    write_json_report(out, report)
    print(f"FILESYSTEM_PERMISSION_PARITY_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
