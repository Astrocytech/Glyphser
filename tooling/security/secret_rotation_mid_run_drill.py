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
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DRILL = ROOT / "governance" / "security" / "secret_rotation_mid_run_drill.json"


def _verify_signed_json(path: Path, findings: list[str]) -> dict[str, Any]:
    if not path.exists():
        findings.append("missing_secret_rotation_mid_run_drill")
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    sig_path = path.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append("missing_secret_rotation_mid_run_drill_signature")
    else:
        sig = sig_path.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(path, sig, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(path, sig, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_secret_rotation_mid_run_drill_signature")
    return payload if isinstance(payload, dict) else {}


def _str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = _verify_signed_json(DRILL, findings)

    status = str(payload.get("status", "")).upper()
    if status != "PASS":
        findings.append(f"drill_not_passed:{status or 'MISSING'}")

    run_id = str(payload.get("run_id", "")).strip()
    if not run_id:
        findings.append("missing_run_id")

    rotated_secret_refs = _str_list(payload.get("rotated_secret_refs", []))
    if not rotated_secret_refs:
        findings.append("missing_rotated_secret_refs")

    gate_behavior = str(payload.get("expected_gate_behavior", "")).strip()
    if not gate_behavior:
        findings.append("missing_expected_gate_behavior")

    resumed_with_new_secret = bool(payload.get("resumed_with_new_secret", False))
    if not resumed_with_new_secret:
        findings.append("run_not_resumed_with_new_secret")

    fallback_uses_old_secret = bool(payload.get("fallback_used_old_secret", False))
    if fallback_uses_old_secret:
        findings.append("fallback_used_old_secret")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "run_id": run_id,
            "rotated_secret_count": len(rotated_secret_refs),
            "resumed_with_new_secret": resumed_with_new_secret,
            "fallback_used_old_secret": fallback_uses_old_secret,
        },
        "metadata": {"gate": "secret_rotation_mid_run_drill"},
    }
    out = evidence_root() / "security" / "secret_rotation_mid_run_drill.json"
    write_json_report(out, report)
    print(f"SECRET_ROTATION_MID_RUN_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
