#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
PROFILE = ROOT / "governance" / "security" / "independent_verifier_profile.json"
DISALLOWED_SHELL_TOKENS = ("&&", "||", ";", "|", "`", "$(", ">", "<")
VERIFIER_CMD_TIMEOUT_SEC = 180.0
VERIFIER_CMD_MAX_OUTPUT_BYTES = 1_000_000


def _looks_safe_for_exec(command: str) -> bool:
    return not any(token in command for token in DISALLOWED_SHELL_TOKENS)


def _run_verification_evidence_command(command: str) -> tuple[bool, str]:
    if not _looks_safe_for_exec(command):
        return False, "unsafe_shell_token"
    try:
        args = shlex.split(command)
    except ValueError:
        return False, "invalid_command_syntax"
    if not args:
        return False, "empty_command"

    env = dict(os.environ)
    env["GLYPHSER_INDEPENDENT_VERIFIER_ROLE"] = "non_maintainer_read_only"
    env["GLYPHSER_INDEPENDENT_VERIFIER_MODE"] = "1"
    result = run_checked(
        args,
        cwd=ROOT,
        env=env,
        timeout_sec=VERIFIER_CMD_TIMEOUT_SEC,
        max_output_bytes=VERIFIER_CMD_MAX_OUTPUT_BYTES,
    )
    if result.returncode != 0:
        return False, f"{getattr(result, 'exit_reason', 'exit')}:{result.returncode}"
    return True, "ok"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not PROFILE.exists():
        findings.append("missing_independent_verifier_profile")
        payload: dict[str, object] = {}
    else:
        payload = json.loads(PROFILE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_independent_verifier_profile")
            payload = {}

    role = str(payload.get("role", "")).strip()
    if role != "read_only_verifier":
        findings.append("invalid_verifier_role")
    commands = payload.get("allowed_commands", [])
    if not isinstance(commands, list) or not commands:
        findings.append("missing_allowed_commands")
        commands = []
    forbidden_patterns = payload.get("forbidden_command_patterns", [])
    if not isinstance(forbidden_patterns, list):
        forbidden_patterns = []

    for cmd in commands:
        if not isinstance(cmd, str) or not cmd.strip():
            findings.append("invalid_allowed_command")
            continue
        lower = cmd.lower()
        for pattern in forbidden_patterns:
            if isinstance(pattern, str) and pattern.strip() and pattern.lower().strip() in lower:
                findings.append(f"forbidden_pattern_in_allowed_command:{cmd}")

    evidence_commands = payload.get("verification_evidence_commands", [])
    if not isinstance(evidence_commands, list) or not evidence_commands:
        findings.append("missing_verification_evidence_commands")
        evidence_commands = []

    command_results: dict[str, str] = {}
    if not findings:
        for cmd in evidence_commands:
            if not isinstance(cmd, str) or not cmd.strip():
                findings.append("invalid_verification_evidence_command")
                continue
            if cmd not in commands:
                findings.append(f"verification_command_not_allowed:{cmd}")
                continue
            ok, reason = _run_verification_evidence_command(cmd)
            command_results[cmd] = reason
            if not ok:
                findings.append(f"verification_command_failed:{cmd}:{reason}")

    runtime_role = os.environ.get("GLYPHSER_INDEPENDENT_VERIFIER_ROLE", "").strip()
    if os.environ.get("GITHUB_ACTIONS") == "true" and runtime_role != "non_maintainer_read_only":
        findings.append("missing_non_maintainer_runtime_role")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "profile_path": str(PROFILE.relative_to(ROOT)).replace("\\", "/"),
            "allowed_commands": len(commands),
            "verification_evidence_commands": len(evidence_commands),
            "command_results": command_results,
            "executor_role": runtime_role or "non_maintainer_read_only",
        },
        "metadata": {"gate": "independent_verifier_profile_gate"},
    }
    out = evidence_root() / "security" / "independent_verifier_profile_gate.json"
    write_json_report(out, report)
    print(f"INDEPENDENT_VERIFIER_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
