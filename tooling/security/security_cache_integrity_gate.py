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

run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

LOCK = ROOT / "tooling" / "security" / "security_toolchain_lock.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _lock_versions() -> dict[str, str]:
    payload = _load_json(LOCK)
    out: dict[str, str] = {}
    for name, spec in payload.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            continue
        version = str(spec.get("version", "")).strip()
        if version:
            out[name.lower()] = version
    return out


def _installed_versions() -> dict[str, str]:
    proc = run_checked([sys.executable, "-m", "pip", "list", "--format", "json"])
    if proc.returncode != 0:
        raise RuntimeError(f"pip list failed: {proc.returncode}")
    payload = json.loads(proc.stdout)
    if not isinstance(payload, list):
        return {}
    out: dict[str, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip().lower()
        version = str(item.get("version", "")).strip()
        if name and version:
            out[name] = version
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    locked = _lock_versions()
    if not locked:
        findings.append("invalid_or_empty_security_toolchain_lock")

    try:
        installed = _installed_versions()
    except Exception:
        installed = {}
        findings.append("unable_to_read_installed_packages")

    for name, version in sorted(locked.items()):
        actual = installed.get(name)
        if actual is None:
            findings.append(f"missing_locked_package:{name}")
            continue
        if actual != version:
            findings.append(f"locked_package_version_mismatch:{name}:expected:{version}:actual:{actual}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "locked_packages": len(locked),
            "checked_packages": len([name for name in locked if name in installed]),
        },
        "metadata": {"gate": "security_cache_integrity_gate", "cache_poisoning_resistant": True},
    }
    out = evidence_root() / "security" / "security_cache_integrity_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_CACHE_INTEGRITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
