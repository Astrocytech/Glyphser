#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "toolchain_source_failover_policy.json"
INSTALL_REPORT = lambda: evidence_root() / "security" / "security_toolchain_install_report.json"
HISTORY = ROOT / "evidence" / "security" / "toolchain_source_failover_history.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _package_entries(install_payload: dict[str, Any]) -> dict[str, dict[str, str]]:
    raw = install_payload.get("install", []) if isinstance(install_payload, dict) else []
    out: dict[str, dict[str, str]] = {}
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata", {})
        dl = item.get("download_info", {})
        if not isinstance(meta, dict) or not isinstance(dl, dict):
            continue
        name = str(meta.get("name", "")).strip().lower()
        if not name:
            continue
        url = str(dl.get("url", "")).strip()
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        hashes = (dl.get("archive_info", {}) if isinstance(dl.get("archive_info", {}), dict) else {}).get("hashes", {})
        sha256 = str(hashes.get("sha256", "")).strip().lower() if isinstance(hashes, dict) else ""
        out[name] = {"host": host, "url": url, "sha256": sha256}
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_toolchain_source_failover_policy")
        policy = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_toolchain_source_failover_policy")

    primary = {
        str(x).strip().lower()
        for x in (policy.get("primary_hosts", []) if isinstance(policy, dict) else [])
        if isinstance(x, str) and str(x).strip()
    }
    mirror = {
        str(x).strip().lower()
        for x in (policy.get("mirror_hosts", []) if isinstance(policy, dict) else [])
        if isinstance(x, str) and str(x).strip()
    }
    allowed_hosts = primary | mirror

    if not primary:
        findings.append("empty_primary_hosts")
    if not mirror:
        findings.append("empty_mirror_hosts")

    report_path = INSTALL_REPORT()
    if not report_path.exists():
        findings.append("missing_security_toolchain_install_report")
        packages = {}
    else:
        try:
            packages = _package_entries(_load_json(report_path))
        except Exception:
            packages = {}
            findings.append("invalid_security_toolchain_install_report")

    history_payload: dict[str, Any] = {}
    if HISTORY.exists():
        try:
            history_payload = _load_json(HISTORY)
        except Exception:
            history_payload = {}
            findings.append("invalid_toolchain_source_failover_history")

    history = history_payload.get("packages", {}) if isinstance(history_payload, dict) else {}
    if not isinstance(history, dict):
        history = {}

    for name, info in sorted(packages.items()):
        host = info.get("host", "")
        sha256 = info.get("sha256", "")
        if host not in allowed_hosts:
            findings.append(f"unapproved_toolchain_source_host:{name}:{host}")

        prior = history.get(name, {}) if isinstance(history.get(name, {}), dict) else {}
        prior_hashes = prior.get("hashes", {}) if isinstance(prior.get("hashes", {}), dict) else {}
        for prev_host, prev_hash in prior_hashes.items():
            if isinstance(prev_hash, str) and prev_hash and sha256 and prev_hash != sha256:
                findings.append(f"integrity_equivalence_violation:{name}:host:{host}:prev_host:{prev_host}")
                break

        hashes = {str(k): str(v) for k, v in prior_hashes.items() if isinstance(k, str) and isinstance(v, str)}
        if host and sha256:
            hashes[host] = sha256
        history[name] = {"hashes": hashes, "last_url": info.get("url", "")}

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps({"schema_version": 1, "packages": history}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    history_snapshot = evidence_root() / "security" / "toolchain_source_failover_history.json"
    history_snapshot.parent.mkdir(parents=True, exist_ok=True)
    history_snapshot.write_text(
        json.dumps({"schema_version": 1, "packages": history}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "packages_checked": len(packages),
            "allowed_hosts": sorted(allowed_hosts),
            "primary_hosts": sorted(primary),
            "mirror_hosts": sorted(mirror),
        },
        "metadata": {"gate": "toolchain_source_failover_gate"},
    }
    out = evidence_root() / "security" / "toolchain_source_failover_gate.json"
    write_json_report(out, report)
    print(f"TOOLCHAIN_SOURCE_FAILOVER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
