#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "runbook_command_health_checks.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checks: list[dict[str, object]] = []

    if not POLICY.exists():
        findings.append("missing_runbook_command_health_policy")
        payload: dict[str, object] = {}
    else:
        payload = json.loads(POLICY.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_runbook_command_health_policy")
            payload = {}

    sig = POLICY.with_suffix(".json.sig")
    if not sig.exists():
        findings.append("missing_runbook_command_health_policy_signature")
    else:
        sig_text = sig.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_runbook_command_health_policy_signature")

    commands = payload.get("commands", [])
    if not isinstance(commands, list):
        commands = []
        findings.append("invalid_runbook_command_entries")

    timeout_sec = int(payload.get("timeout_sec", 20)) if isinstance(payload.get("timeout_sec"), int) else 20
    max_output_bytes = int(payload.get("max_output_bytes", 100000)) if isinstance(payload.get("max_output_bytes"), int) else 100000

    for idx, row in enumerate(commands, start=1):
        if not isinstance(row, dict):
            findings.append(f"invalid_runbook_command_row:{idx}")
            continue
        cmd = row.get("cmd", [])
        if not isinstance(cmd, list) or not all(isinstance(x, str) and x for x in cmd):
            findings.append(f"invalid_runbook_command_row_cmd:{idx}")
            continue
        proc = run_checked(cmd, cwd=ROOT, timeout_sec=timeout_sec, max_output_bytes=max_output_bytes)
        ok = proc.returncode == 0
        checks.append({"cmd": cmd, "returncode": proc.returncode, "ok": ok})
        if not ok:
            findings.append(f"runbook_command_failed:{idx}:{' '.join(cmd)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"commands_checked": len(checks), "configured_commands": len(commands)},
        "metadata": {"gate": "runbook_command_health_gate"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "runbook_command_health_gate.json"
    write_json_report(out, report)
    print(f"RUNBOOK_COMMAND_HEALTH_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
