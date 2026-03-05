#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "developer_mode_profile.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_attestations(raw: str) -> list[str]:
    text = raw.strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except Exception:
        return [item.strip() for item in text.split(",") if item.strip()]
    if isinstance(payload, list):
        return [str(item).strip() for item in payload if str(item).strip()]
    return []


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_developer_mode_profile_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    profile = os.environ.get("GLYPHSER_SECURITY_PROFILE", "").strip().lower()
    in_dev_mode = profile == "developer"

    required_env = policy.get("required_strict_env_vars", []) if isinstance(policy, dict) else []
    allowed = policy.get("allowed_mock_attestations", []) if isinstance(policy, dict) else []
    mock_env_name = str(policy.get("mock_attestations_env", "GLYPHSER_MOCK_ATTESTATIONS")).strip() or "GLYPHSER_MOCK_ATTESTATIONS"

    if not isinstance(required_env, list):
        required_env = []
        findings.append("invalid_required_strict_env_vars")
    if not isinstance(allowed, list):
        allowed = []
        findings.append("invalid_allowed_mock_attestations")

    required_env = [str(item).strip() for item in required_env if str(item).strip()]
    allowed_set = {str(item).strip() for item in allowed if str(item).strip()}

    used_attestations: list[str] = []
    if in_dev_mode:
        for name in required_env:
            if not _is_truthy(os.environ.get(name, "")):
                findings.append(f"missing_required_strict_env:{name}")

        used_attestations = _parse_attestations(os.environ.get(mock_env_name, ""))
        if not used_attestations:
            findings.append("missing_explicit_mock_attestations")
        for item in used_attestations:
            if item not in allowed_set:
                findings.append(f"unapproved_mock_attestation:{item}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "profile": profile or "unset",
            "developer_mode_active": in_dev_mode,
            "required_strict_env_vars": required_env,
            "mock_attestations_env": mock_env_name,
            "used_mock_attestations": used_attestations,
            "allowed_mock_attestations": sorted(allowed_set),
        },
        "metadata": {"gate": "developer_mode_profile_gate"},
    }
    out = evidence_root() / "security" / "developer_mode_profile_gate.json"
    write_json_report(out, report)
    print(f"DEVELOPER_MODE_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
