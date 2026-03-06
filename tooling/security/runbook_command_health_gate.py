#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import shlex
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
RUNBOOK_DOC_ROOTS: tuple[Path, ...] | None = None
RUNBOOK_CMD_RE = re.compile(r"(python|python3)\s+(tooling/security/[A-Za-z0-9_.\-/]+\.py)(?:\s+([^`\n]+))?")
HELP_FLAG_RE = re.compile(r"--[A-Za-z0-9][A-Za-z0-9-]*")


def _extract_runbook_commands() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    roots = RUNBOOK_DOC_ROOTS if RUNBOOK_DOC_ROOTS is not None else (ROOT / "governance" / "security", ROOT / "docs")
    for root in roots:
        if not root.exists():
            continue
        for doc in sorted(root.rglob("*.md")):
            rel = str(doc.relative_to(ROOT)).replace("\\", "/")
            for line_no, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
                for match in RUNBOOK_CMD_RE.finditer(line):
                    runner = match.group(1)
                    script = match.group(2)
                    tail = match.group(3) or ""
                    cmd_text = f"{runner} {script}".strip()
                    if tail.strip():
                        cmd_text = f"{cmd_text} {tail.strip()}"
                    try:
                        tokens = shlex.split(cmd_text)
                    except ValueError:
                        continue
                    if len(tokens) >= 2:
                        rows.append({"doc": rel, "line": line_no, "script": script, "cmd": tokens})
    return rows


def _help_flags(script_path: str, *, timeout_sec: int, max_output_bytes: int) -> tuple[set[str], bool]:
    proc = run_checked([sys.executable, script_path, "--help"], cwd=ROOT, timeout_sec=timeout_sec, max_output_bytes=max_output_bytes)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return set(HELP_FLAG_RE.findall(out)), proc.returncode == 0


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

    runbook_examples = _extract_runbook_commands()
    help_cache: dict[str, tuple[set[str], bool]] = {}
    for row in runbook_examples:
        script = str(row.get("script", "")).strip()
        if not script:
            continue
        if script not in help_cache:
            help_cache[script] = _help_flags(script, timeout_sec=timeout_sec, max_output_bytes=max_output_bytes)
        allowed_flags, ok = help_cache[script]
        if not ok:
            findings.append(f"runbook_cli_help_unavailable:{script}")
            continue
        cmd = row.get("cmd", [])
        if not isinstance(cmd, list):
            continue
        options = [str(token).split("=", 1)[0] for token in cmd[2:] if isinstance(token, str) and token.startswith("--")]
        for opt in options:
            if opt not in allowed_flags:
                findings.append(
                    f"runbook_option_not_supported:{row['doc']}:{row['line']}:{script}:{opt}"
                )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "commands_checked": len(checks),
            "configured_commands": len(commands),
            "runbook_examples_checked": len(runbook_examples),
            "scripts_with_help_checked": len(help_cache),
        },
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
