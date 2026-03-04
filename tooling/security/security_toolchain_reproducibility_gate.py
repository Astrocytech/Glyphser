#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _parse_freeze(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        out[name.lower()] = version.strip()
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    lock_path = ROOT / "tooling" / "security" / "security_toolchain_lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(lock, dict):
        raise ValueError("invalid security toolchain lock")

    proc = run_checked([sys.executable, "-m", "pip", "freeze", "--all"], cwd=ROOT)
    installed = _parse_freeze(proc.stdout if proc.returncode == 0 else "")
    findings: list[str] = []
    fingerprint_rows: list[str] = []
    checks: dict[str, dict[str, str | bool]] = {}

    for package in sorted(lock):
        spec = lock.get(package, {})
        if not isinstance(spec, dict):
            findings.append(f"invalid_lock_entry:{package}")
            continue
        expected = str(spec.get("version", "")).strip()
        observed = installed.get(package.lower(), "")
        ok = bool(observed) and observed == expected
        checks[package] = {"ok": ok, "expected": expected, "observed": observed or "missing"}
        if not ok:
            findings.append(f"toolchain_version_mismatch:{package}:{observed or 'missing'}:{expected}")
        fingerprint_rows.append(f"{package}=={observed or 'missing'}")

    fingerprint = hashlib.sha256("\n".join(sorted(fingerprint_rows)).encode("utf-8")).hexdigest()
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"locked_packages": len(lock), "fingerprint_sha256": fingerprint},
        "metadata": {"gate": "security_toolchain_reproducibility_gate"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "security_toolchain_reproducibility_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_TOOLCHAIN_REPRODUCIBILITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
