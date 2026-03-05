#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import tarfile
import tempfile
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay an incident bundle locally and summarize critical statuses.")
    parser.add_argument("--bundle", required=True)
    args = parser.parse_args([] if argv is None else argv)

    bundle_path = Path(args.bundle)
    if not bundle_path.is_absolute():
        bundle_path = (ROOT / bundle_path).resolve()
    if not bundle_path.exists():
        raise FileNotFoundError(f"missing bundle: {bundle_path}")

    findings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="glyphser-tabletop-") as td:
        td_path = Path(td)
        with tarfile.open(bundle_path, "r:gz") as tf:
            tf.extractall(td_path, filter="data")
        sec = td_path / "security"
        checks = {
            "policy_signature": _status(sec / "policy_signature.json"),
            "provenance_signature": _status(sec / "provenance_signature.json"),
            "evidence_attestation_gate": _status(sec / "evidence_attestation_gate.json"),
            "provenance_revocation_gate": _status(sec / "provenance_revocation_gate.json"),
        }
        for key, status in checks.items():
            if status != "PASS":
                findings.append(f"tabletop_replay_check_not_pass:{key}:{status}")

    payload: dict[str, Any] = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "bundle": str(bundle_path.relative_to(ROOT)).replace("\\", "/")
            if str(bundle_path).startswith(str(ROOT))
            else str(bundle_path),
        },
        "metadata": {"gate": "tabletop_replay"},
    }
    out = evidence_root() / "security" / "tabletop_replay.json"
    write_json_report(out, payload)
    print(f"TABLETOP_REPLAY: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
