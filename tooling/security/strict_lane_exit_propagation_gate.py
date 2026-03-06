#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

STRICT_LANE_WORKFLOWS = (
    ".github/workflows/ci.yml",
    ".github/workflows/security-maintenance.yml",
    ".github/workflows/release.yml",
)
CRITICAL_STRICT_COMMANDS = (
    "tooling/security/policy_signature_gate.py",
    "tooling/security/provenance_signature_gate.py",
    "tooling/security/evidence_attestation_gate.py",
    "tooling/security/security_super_gate.py",
)
MASKED_EXIT_RE = re.compile(r"\|\|\s*(?:true|:|exit\s+0)\b|;\s*true\b|\bset\s+\+e\b")


def _step_blocks(text: str) -> list[tuple[int, list[str]]]:
    blocks: list[tuple[int, list[str]]] = []
    current: list[str] = []
    start_line = 1
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("- name:"):
            if current:
                blocks.append((start_line, current))
            current = [line]
            start_line = line_no
            continue
        if current:
            current.append(line)
    if current:
        blocks.append((start_line, current))
    return blocks


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_blocks = 0

    for rel in STRICT_LANE_WORKFLOWS:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        blocks = _step_blocks(path.read_text(encoding="utf-8"))
        for start_line, block in blocks:
            checked_blocks += 1
            block_text = "\n".join(block)
            has_continue_on_error = any(
                line.strip().startswith("continue-on-error:") and "true" in line.lower() for line in block
            )
            for script in CRITICAL_STRICT_COMMANDS:
                if script not in block_text:
                    continue
                if has_continue_on_error:
                    findings.append(f"critical_exit_masked_continue_on_error:{rel}:{start_line}:{script}")
                for idx, line in enumerate(block, start=start_line):
                    if script in line and MASKED_EXIT_RE.search(line):
                        findings.append(f"critical_exit_masked_shell:{rel}:{idx}:{script}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_checked": len(STRICT_LANE_WORKFLOWS),
            "step_blocks_checked": checked_blocks,
            "critical_commands": len(CRITICAL_STRICT_COMMANDS),
        },
        "metadata": {"gate": "strict_lane_exit_propagation_gate"},
    }
    out = evidence_root() / "security" / "strict_lane_exit_propagation_gate.json"
    write_json_report(out, report)
    print(f"STRICT_LANE_EXIT_PROPAGATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
