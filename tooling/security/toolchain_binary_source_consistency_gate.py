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

LOCK = ROOT / "tooling" / "security" / "security_toolchain_lock.json"
INSTALL_REPORT = ROOT / "evidence" / "security" / "security_toolchain_install_report.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _locked_hashes() -> dict[str, str]:
    payload = _load_json(LOCK)
    out: dict[str, str] = {}
    for name, spec in payload.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            continue
        raw = str(spec.get("version_hash", "")).strip().lower()
        if raw.startswith("sha256:"):
            out[name.lower()] = raw.split(":", 1)[1]
    return out


def _report_hashes(report: dict[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    installs = report.get("install", []) if isinstance(report, dict) else []
    if not isinstance(installs, list):
        installs = []

    for item in installs:
        if not isinstance(item, dict):
            continue
        metadata = item.get("metadata", {})
        name = str(metadata.get("name", "")).strip().lower() if isinstance(metadata, dict) else ""
        if not name:
            continue
        hashes = out.setdefault(name, set())
        download_info = item.get("download_info", {})
        archive_info = download_info.get("archive_info", {}) if isinstance(download_info, dict) else {}
        if isinstance(archive_info, dict):
            hashes_dict = archive_info.get("hashes", {})
            if isinstance(hashes_dict, dict):
                for algo, value in hashes_dict.items():
                    if str(algo).lower() == "sha256" and str(value).strip():
                        hashes.add(str(value).strip().lower())
            fallback = str(archive_info.get("hash", "")).strip().lower()
            if fallback.startswith("sha256="):
                hashes.add(fallback.split("=", 1)[1])
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not LOCK.exists():
        findings.append("missing_security_toolchain_lock")
        locked = {}
    else:
        locked = _locked_hashes()

    if not INSTALL_REPORT.exists():
        findings.append("missing_security_toolchain_install_report")
        observed: dict[str, set[str]] = {}
    else:
        observed = _report_hashes(_load_json(INSTALL_REPORT))

    for name, expected_hash in sorted(locked.items()):
        seen = observed.get(name, set())
        if not seen:
            findings.append(f"missing_installed_hash_observation:{name}")
            continue
        if expected_hash not in seen:
            findings.append(f"binary_source_hash_mismatch:{name}:expected:{expected_hash}:observed:{','.join(sorted(seen))}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "locked_tools": len(locked),
            "observed_tools": len(observed),
        },
        "metadata": {"gate": "toolchain_binary_source_consistency_gate"},
    }
    out = evidence_root() / "security" / "toolchain_binary_source_consistency_gate.json"
    write_json_report(out, report)
    print(f"TOOLCHAIN_BINARY_SOURCE_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
