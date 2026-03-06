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

RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
SIGNATURE_SENSITIVE_SCRIPTS = (
    "policy_signature_generate.py",
    "policy_signature_gate.py",
    "provenance_signature_gate.py",
    "evidence_attestation_index.py",
    "evidence_attestation_gate.py",
    "security_super_gate.py",
    "third_party_pentest_gate.py",
    "formal_security_review_artifact.py",
)
PY_CMD_RE = re.compile(r"python\s+tooling/security/([A-Za-z0-9_]+\.py)(?P<args>[^\n]*)")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0

    if not RELEASE_WORKFLOW.exists():
        findings.append("missing_release_workflow:.github/workflows/release.yml")
        text = ""
    else:
        text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    seen_scripts: set[str] = set()
    for match in PY_CMD_RE.finditer(text):
        script = match.group(1)
        if script not in SIGNATURE_SENSITIVE_SCRIPTS:
            continue
        seen_scripts.add(script)
        checked += 1
        args = str(match.group("args") or "")
        if "--strict-key" not in args:
            findings.append(f"signature_sensitive_step_missing_strict_key:{script}")

    for script in SIGNATURE_SENSITIVE_SCRIPTS:
        if script not in seen_scripts:
            findings.append(f"missing_signature_sensitive_step:{script}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "signature_sensitive_steps_checked": checked,
            "required_signature_sensitive_steps": len(SIGNATURE_SENSITIVE_SCRIPTS),
        },
        "metadata": {"gate": "release_strict_key_mode_gate"},
    }
    out = evidence_root() / "security" / "release_strict_key_mode_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_STRICT_KEY_MODE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
