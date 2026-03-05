#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOW_CONTROLS: dict[str, list[str]] = {
    ".github/workflows/ci.yml": [
        "python tooling/security/policy_signature_gate.py --strict-key",
        "python tooling/security/provenance_signature_gate.py --strict-key",
        "python tooling/security/evidence_attestation_gate.py --strict-key",
        "python tooling/security/security_verification_summary.py --strict-key",
        "python tooling/security/security_super_gate.py --strict-key",
    ],
    ".github/workflows/security-maintenance.yml": [
        "python tooling/security/policy_signature_gate.py --strict-key",
        "python tooling/security/provenance_signature_gate.py --strict-key",
        "python tooling/security/evidence_attestation_gate.py --strict-key",
        "python tooling/security/security_verification_summary.py --strict-key",
        "python tooling/security/security_super_gate.py --strict-key",
    ],
    ".github/workflows/release.yml": [
        "python tooling/security/policy_signature_gate.py --strict-key",
        "python tooling/security/provenance_signature_gate.py --strict-key",
        "python tooling/security/evidence_attestation_gate.py --strict-key",
        "python tooling/security/security_super_gate.py --strict-key",
    ],
}


def _step_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("- name:"):
            if current:
                blocks.append(current)
            current = [line]
            continue
        if current:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_controls = 0

    for rel, controls in WORKFLOW_CONTROLS.items():
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        blocks = _step_blocks(text)
        for control in controls:
            checked_controls += 1
            matched = False
            for block in blocks:
                body = "\n".join(block)
                if control not in body:
                    continue
                matched = True
                for line in block:
                    if line.strip().startswith("if:"):
                        findings.append(f"conditional_critical_control:{rel}:{control}")
                        break
            if not matched:
                findings.append(f"missing_critical_control:{rel}:{control}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_controls": checked_controls, "workflows_checked": len(WORKFLOW_CONTROLS)},
        "metadata": {"gate": "required_control_condition_bypass_gate"},
    }
    out = evidence_root() / "security" / "required_control_condition_bypass_gate.json"
    write_json_report(out, report)
    print(f"REQUIRED_CONTROL_CONDITION_BYPASS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
