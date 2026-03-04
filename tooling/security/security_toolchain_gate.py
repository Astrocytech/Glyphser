#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    lock = json.loads((ROOT / "tooling" / "security" / "security_toolchain_lock.json").read_text(encoding="utf-8"))
    transitive_path = ROOT / "tooling" / "security" / "security_toolchain_transitive_lock.json"
    if transitive_path.exists():
        transitive_lock = json.loads(transitive_path.read_text(encoding="utf-8"))
    else:
        transitive_lock = {}
    if not isinstance(lock, dict):
        raise ValueError("invalid security toolchain lock")
    if not isinstance(transitive_lock, dict):
        raise ValueError("invalid transitive lock")

    findings: list[str] = []
    checks: dict[str, dict[str, str | bool]] = {}
    for package, spec in lock.items():
        if not isinstance(package, str) or not isinstance(spec, dict):
            findings.append("invalid lock entry")
            continue
        want_version = str(spec.get("version", "")).strip()
        want_hash = str(spec.get("version_hash", "")).strip().lower()
        try:
            installed = metadata.version(package)
        except metadata.PackageNotFoundError:
            checks[package] = {"ok": False, "reason": "not_installed"}
            findings.append(f"{package} not installed")
            continue

        observed_hash = "sha256:" + _sha256_text(f"{package}=={installed}")
        ok = installed == want_version and observed_hash == want_hash
        checks[package] = {
            "ok": ok,
            "installed": installed,
            "expected": want_version,
            "observed_hash": observed_hash,
            "expected_hash": want_hash,
        }
        if not ok:
            findings.append(f"{package} version/hash mismatch")
        if transitive_path.exists():
            transitive = transitive_lock.get(package, {})
            if not isinstance(transitive, dict) or not isinstance(transitive.get("transitive", []), list):
                findings.append(f"{package} missing transitive lock entry")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checks": checks,
        "summary": {"locked_packages": len(lock), "has_transitive_lock": transitive_path.exists()},
        "metadata": {"gate": "security_toolchain_gate"},
    }
    out = evidence_root() / "security" / "security_toolchain.json"
    write_json_report(out, payload)
    print(f"SECURITY_TOOLCHAIN_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
