#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from packaging.utils import InvalidWheelFilename, canonicalize_name, parse_wheel_filename

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

LOCK = ROOT / "tooling" / "security" / "security_toolchain_lock.json"
ALLOWED_HOSTS = {"files.pythonhosted.org", "pypi.org"}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _lock_data() -> dict[str, dict[str, str]]:
    payload = _load_json(LOCK)
    out: dict[str, dict[str, str]] = {}
    for name, spec in payload.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            continue
        version = str(spec.get("version", "")).strip()
        version_hash = str(spec.get("version_hash", "")).strip()
        if version and version_hash.startswith("sha256:"):
            out[name.lower()] = {"version": version, "sha256": version_hash.split(":", 1)[1]}
    return out


def _report_packages(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = payload.get("install", []) if isinstance(payload, dict) else []
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata", {})
        if not isinstance(meta, dict):
            continue
        name = str(meta.get("name", "")).strip().lower()
        version = str(meta.get("version", "")).strip()
        if not name or not version:
            continue
        out[name] = item
    return out


def _download_hash(item: dict[str, Any]) -> str:
    dlinfo = item.get("download_info", {}) if isinstance(item, dict) else {}
    if not isinstance(dlinfo, dict):
        return ""
    archive = dlinfo.get("archive_info", {})
    if not isinstance(archive, dict):
        return ""
    hashes = archive.get("hashes", {})
    if not isinstance(hashes, dict):
        return ""
    return str(hashes.get("sha256", "")).strip().lower()


def _download_url(item: dict[str, Any]) -> str:
    dlinfo = item.get("download_info", {}) if isinstance(item, dict) else {}
    return str(dlinfo.get("url", "")).strip() if isinstance(dlinfo, dict) else ""


def _wheel_filename(url: str) -> str:
    parsed = urlparse(url)
    return Path(parsed.path).name if parsed.path else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    report_path = evidence_root() / "security" / "security_toolchain_install_report.json"

    lock = _lock_data()
    if not lock:
        findings.append("invalid_or_empty_security_toolchain_lock")

    if not report_path.exists():
        findings.append("missing_security_toolchain_install_report")
        install = {}
    else:
        try:
            install = _report_packages(_load_json(report_path))
        except Exception:
            install = {}
            findings.append("invalid_security_toolchain_install_report")

    for name, spec in sorted(lock.items()):
        item = install.get(name)
        if item is None:
            findings.append(f"missing_provenance_entry:{name}")
            continue

        meta = item.get("metadata", {}) if isinstance(item, dict) else {}
        actual_version = str(meta.get("version", "")).strip() if isinstance(meta, dict) else ""
        if actual_version != spec["version"]:
            findings.append(f"version_mismatch:{name}:expected:{spec['version']}:actual:{actual_version}")

        actual_hash = _download_hash(item)
        if actual_hash != spec["sha256"]:
            findings.append(f"hash_mismatch:{name}:expected:{spec['sha256']}:actual:{actual_hash}")

        url = _download_url(item)
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        if parsed.scheme != "https" or host not in ALLOWED_HOSTS:
            findings.append(f"unapproved_download_source:{name}:{url}")
        wheel_name = _wheel_filename(url)
        if not wheel_name.endswith(".whl"):
            findings.append(f"non_wheel_distribution:{name}:{wheel_name or 'missing'}")
        else:
            try:
                wheel_dist, wheel_version, _, _ = parse_wheel_filename(wheel_name)
            except InvalidWheelFilename:
                findings.append(f"invalid_wheel_filename:{name}:{wheel_name}")
            else:
                if canonicalize_name(str(wheel_dist)) != canonicalize_name(name):
                    findings.append(f"wheel_metadata_name_mismatch:{name}:wheel:{wheel_dist}")
                if str(wheel_version) != spec["version"]:
                    findings.append(f"wheel_metadata_version_mismatch:{name}:wheel:{wheel_version}:lock:{spec['version']}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "locked_packages": len(lock),
            "provenance_entries": len(install),
            "install_report": str(report_path),
            "allowed_hosts": sorted(ALLOWED_HOSTS),
        },
        "metadata": {"gate": "toolchain_dependency_provenance_gate"},
    }
    out = evidence_root() / "security" / "toolchain_dependency_provenance_gate.json"
    write_json_report(out, report)
    print(f"TOOLCHAIN_DEPENDENCY_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
