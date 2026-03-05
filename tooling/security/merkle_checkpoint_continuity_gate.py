#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

_HEX_256 = re.compile(r"^[0-9a-f]{64}$")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    checkpoint_path = sec / "rolling_merkle_checkpoints.json"
    report = _load_json(checkpoint_path)

    findings: list[str] = []
    expected_previous = os.environ.get("GLYPHSER_EXPECTED_PREVIOUS_MERKLE_ROOT", "").strip().lower()
    if not expected_previous:
        findings.append("missing_expected_previous_root")
    elif not _HEX_256.fullmatch(expected_previous):
        findings.append("invalid_expected_previous_root_hex")

    if not checkpoint_path.exists():
        findings.append("missing_rolling_merkle_checkpoint")

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    checkpoint_previous = str(summary.get("previous_root", "")).strip().lower()
    checkpoint_final = str(summary.get("final_root", "")).strip().lower()

    if checkpoint_path.exists() and report.get("status") != "PASS":
        findings.append("rolling_merkle_checkpoint_not_pass")
    if checkpoint_path.exists() and not checkpoint_previous:
        findings.append("missing_checkpoint_previous_root")
    if checkpoint_previous and not _HEX_256.fullmatch(checkpoint_previous):
        findings.append("invalid_checkpoint_previous_root_hex")
    if checkpoint_final and not _HEX_256.fullmatch(checkpoint_final):
        findings.append("invalid_checkpoint_final_root_hex")
    if expected_previous and checkpoint_previous and expected_previous != checkpoint_previous:
        findings.append("checkpoint_continuity_mismatch")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "expected_previous_root": expected_previous,
            "checkpoint_previous_root": checkpoint_previous,
            "checkpoint_final_root": checkpoint_final,
            "checkpoint_path": str(checkpoint_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "merkle_checkpoint_continuity_gate"},
    }
    out = sec / "merkle_checkpoint_continuity_gate.json"
    write_json_report(out, payload)
    print(f"MERKLE_CHECKPOINT_CONTINUITY_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
