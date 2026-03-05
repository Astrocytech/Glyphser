#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXTERNAL_EXPORT_ARTIFACTS = [
    "evidence/security/security_dashboard.json",
    "evidence/security/security_events.jsonl",
    "evidence/security/offline_verify_bundle_export.json",
    "evidence/security/offline_verify_bundle/export_manifest.json",
]
SENSITIVE_KEYWORDS = ("token", "secret", "password", "authorization", "api_key", "private_key", "credential")
SENSITIVE_VALUE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bearer_token_value", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{8,}")),
    ("github_pat", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("generic_api_key_assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[^,\s]{4,}")),
]


def _walk(payload: Any, path: str, findings: list[str]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_s = str(key)
            key_l = key_s.lower()
            if any(marker in key_l for marker in SENSITIVE_KEYWORDS):
                findings.append(f"sensitive_key:{path}.{key_s}")
            _walk(value, f"{path}.{key_s}", findings)
        return
    if isinstance(payload, list):
        for idx, value in enumerate(payload):
            _walk(value, f"{path}[{idx}]", findings)
        return
    if isinstance(payload, str):
        for label, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(payload):
                findings.append(f"sensitive_value:{path}:{label}")


def _scan_json(path: Path, findings: list[str]) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        findings.append(f"invalid_json_external_export:{rel}:{type(exc).__name__}")
        return
    _walk(payload, "$", findings)


def _scan_jsonl(path: Path, findings: list[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        findings.append(f"unreadable_jsonl_external_export:{rel}:{type(exc).__name__}")
        return
    for idx, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except ValueError:
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            findings.append(f"invalid_jsonl_line_external_export:{rel}:{idx}")
            continue
        _walk(payload, f"$[{idx}]", findings)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned: list[str] = []

    for rel in EXTERNAL_EXPORT_ARTIFACTS:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_external_export_artifact:{rel}")
            continue
        scanned.append(rel)
        if path.suffix == ".jsonl":
            _scan_jsonl(path, findings)
        else:
            _scan_json(path, findings)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(findings),
        "summary": {
            "scanned_artifact_count": len(scanned),
            "required_artifact_count": len(EXTERNAL_EXPORT_ARTIFACTS),
            "scanned_artifacts": scanned,
        },
        "metadata": {"gate": "external_export_data_minimization_gate"},
    }
    out = evidence_root() / "security" / "external_export_data_minimization_gate.json"
    write_json_report(out, report)
    print(f"EXTERNAL_EXPORT_DATA_MINIMIZATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
