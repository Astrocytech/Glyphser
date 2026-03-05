#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "pii_minimization_policy.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    sig = POLICY.with_suffix(".json.sig")
    sig_text = sig.read_text(encoding="utf-8").strip()
    if not artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.current_key(strict=False)):
        if not artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.bootstrap_key()):
            findings.append("invalid_pii_minimization_policy_signature")

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        findings.append("invalid_pii_minimization_policy")
        policy = {}

    globs = policy.get("scan_globs", []) if isinstance(policy.get("scan_globs"), list) else []
    patterns = policy.get("forbidden_patterns", {}) if isinstance(policy.get("forbidden_patterns"), dict) else {}
    allowed_tokens = {
        str(item).lower()
        for item in policy.get("allowed_tokens", [])
        if isinstance(item, str) and str(item).strip()
    }

    compiled: dict[str, re.Pattern[str]] = {}
    for name, pattern in patterns.items():
        if isinstance(name, str) and isinstance(pattern, str):
            compiled[name] = re.compile(pattern)

    scanned = 0
    for glob in globs:
        if not isinstance(glob, str) or not glob.strip():
            continue
        for path in sorted(ROOT.glob(glob)):
            if not path.is_file():
                continue
            scanned += 1
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for token in allowed_tokens:
                lowered = lowered.replace(token, "")
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            for name, regex in compiled.items():
                if regex.search(lowered):
                    findings.append(f"pii_pattern_detected:{name}:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_files": scanned,
            "pattern_count": len(compiled),
        },
        "metadata": {"gate": "pii_minimization_gate"},
    }
    out = evidence_root() / "security" / "pii_minimization_gate.json"
    write_json_report(out, report)
    print(f"PII_MINIMIZATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
