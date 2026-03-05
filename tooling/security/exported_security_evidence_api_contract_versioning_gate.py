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

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "exported_security_evidence_api_contract_policy.json"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _json_path_get(payload: dict[str, Any], dotted: str) -> str:
    current: Any = payload
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return ""
        current = current[part]
    return str(current) if isinstance(current, str) else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _read_json(POLICY)
    if not policy:
        findings.append("missing_or_invalid_exported_security_evidence_api_contract_policy")
        allowed_versions: set[str] = set()
        current_version = ""
        required_exports: list[dict[str, Any]] = []
    else:
        allowed_versions = {
            str(item).strip()
            for item in policy.get("allowed_versions", [])
            if isinstance(item, str) and str(item).strip()
        }
        current_version = str(policy.get("current_api_contract_version", "")).strip()
        required_exports = [
            item for item in policy.get("required_exports", []) if isinstance(item, dict)
        ] if isinstance(policy.get("required_exports"), list) else []

    if not current_version:
        findings.append("missing_current_api_contract_version")
    if allowed_versions and current_version and current_version not in allowed_versions:
        findings.append("current_api_contract_version_not_allowed")

    checked = 0
    for cfg in required_exports:
        artifact = str(cfg.get("artifact", "")).strip()
        kind = str(cfg.get("kind", "")).strip()
        if not artifact or kind not in {"json", "jsonl"}:
            findings.append("invalid_required_export_entry")
            continue
        path = ROOT / artifact
        if not path.exists():
            findings.append(f"missing_exported_security_evidence:{artifact}")
            continue

        checked += 1
        if kind == "json":
            version_path = str(cfg.get("version_path", "")).strip()
            if not version_path:
                findings.append(f"missing_version_path:{artifact}")
                continue
            version = _json_path_get(_read_json(path), version_path)
            if not version:
                findings.append(f"missing_api_contract_version:{artifact}:{version_path}")
                continue
            if allowed_versions and version not in allowed_versions:
                findings.append(f"unsupported_api_contract_version:{artifact}:{version}")
            if current_version and version != current_version:
                findings.append(f"stale_api_contract_version:{artifact}:{version}")
            continue

        version_field = str(cfg.get("version_field", "")).strip()
        if not version_field:
            findings.append(f"missing_version_field:{artifact}")
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            findings.append(f"unreadable_exported_security_evidence:{artifact}")
            continue
        for idx, raw in enumerate(lines, start=1):
            if not raw.strip():
                continue
            try:
                entry = json.loads(raw)
            except ValueError:
                findings.append(f"invalid_jsonl_exported_security_evidence:{artifact}:{idx}")
                continue
            if not isinstance(entry, dict):
                findings.append(f"invalid_jsonl_record:{artifact}:{idx}")
                continue
            version = str(entry.get(version_field, "")).strip()
            if not version:
                findings.append(f"missing_api_contract_version:{artifact}:{idx}:{version_field}")
                continue
            if allowed_versions and version not in allowed_versions:
                findings.append(f"unsupported_api_contract_version:{artifact}:{idx}:{version}")
            if current_version and version != current_version:
                findings.append(f"stale_api_contract_version:{artifact}:{idx}:{version}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(findings),
        "summary": {
            "policy": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
            "required_exports": len(required_exports),
            "checked_exports": checked,
            "current_api_contract_version": current_version,
            "allowed_versions": sorted(allowed_versions),
        },
        "metadata": {"gate": "exported_security_evidence_api_contract_versioning_gate"},
    }
    out = evidence_root() / "security" / "exported_security_evidence_api_contract_versioning_gate.json"
    write_json_report(out, report)
    print(f"EXPORTED_SECURITY_EVIDENCE_API_CONTRACT_VERSIONING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
