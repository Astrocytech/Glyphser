#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
CONTROL_MAP = ROOT / "governance" / "security" / "threat_model_control_map.json"
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9._:/-]+$")


def _is_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _check_identifier(kind: str, value: str, findings: list[str]) -> None:
    normalized = unicodedata.normalize("NFKC", value)
    if normalized != value:
        findings.append(f"identifier_nfkc_variant:{kind}:{value}")
    if not _is_ascii(value):
        findings.append(f"identifier_non_ascii:{kind}:{value}")
    if not IDENTIFIER_RE.match(value):
        findings.append(f"identifier_invalid_charset:{kind}:{value}")


def _scan_filenames(findings: list[str]) -> int:
    scanned = 0
    roots = [
        ROOT / "governance" / "security",
        ROOT / "tooling" / "security",
        ROOT / ".github" / "workflows",
    ]
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            scanned += 1
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            filename = path.name
            if unicodedata.normalize("NFKC", filename) != filename:
                findings.append(f"filename_nfkc_variant:{rel}")
            if not _is_ascii(filename):
                findings.append(f"filename_non_ascii:{rel}")
    return scanned


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _scan_manifest_identifiers(findings: list[str]) -> int:
    if not MANIFEST.exists():
        findings.append("missing_security_super_gate_manifest")
        return 0
    payload = _load_json(MANIFEST)
    scanned = 0
    for group in ("core", "extended"):
        items = payload.get(group, [])
        if not isinstance(items, list):
            findings.append(f"invalid_manifest_group:{group}")
            continue
        for item in items:
            if not isinstance(item, str):
                findings.append(f"invalid_manifest_identifier:{group}")
                continue
            scanned += 1
            _check_identifier(f"manifest_{group}", item, findings)
    return scanned


def _scan_control_map_identifiers(findings: list[str]) -> int:
    if not CONTROL_MAP.exists():
        return 0
    payload = _load_json(CONTROL_MAP)
    controls = payload.get("controls", []) if isinstance(payload, dict) else []
    if not isinstance(controls, list):
        findings.append("invalid_threat_model_control_map_controls")
        return 0
    scanned = 0
    for item in controls:
        if not isinstance(item, dict):
            continue
        cid = item.get("control_id")
        gate = item.get("gate")
        if isinstance(cid, str):
            scanned += 1
            _check_identifier("control_id", cid, findings)
        if isinstance(gate, str):
            scanned += 1
            _check_identifier("control_gate", gate, findings)
    return scanned


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned_files = _scan_filenames(findings)
    scanned_identifiers = _scan_manifest_identifiers(findings) + _scan_control_map_identifiers(findings)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(findings),
        "summary": {
            "scanned_files": scanned_files,
            "scanned_identifiers": scanned_identifiers,
        },
        "metadata": {"gate": "unicode_confusable_detection_gate"},
    }
    out = evidence_root() / "security" / "unicode_confusable_detection_gate.json"
    write_json_report(out, report)
    print(f"UNICODE_CONFUSABLE_DETECTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
