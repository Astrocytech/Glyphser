#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import importlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from packaging.tags import Tag, sys_tags
from packaging.utils import InvalidWheelFilename, parse_wheel_filename

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_install_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
    raw = payload.get("install", [])
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(item)
    return out


def _wheel_tags_from_download_url(url: str) -> tuple[str, set[Tag]]:
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename:
        return "", set()
    if not filename.endswith(".whl"):
        return filename, set()
    try:
        _, _, _, tags = parse_wheel_filename(filename)
    except InvalidWheelFilename:
        return filename, set()
    return filename, set(tags)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    lock = json.loads((ROOT / "tooling" / "security" / "security_toolchain_lock.json").read_text(encoding="utf-8"))
    install_report_path = evidence_root() / "security" / "security_toolchain_install_report.json"
    install_entries = _load_install_entries(install_report_path)
    install_report: dict[str, dict] = {}
    install_versions: dict[str, set[str]] = {}
    install_requested: set[str] = set()
    for item in install_entries:
        item_meta = item.get("metadata", {})
        if not isinstance(item_meta, dict):
            continue
        name = str(item_meta.get("name", "")).strip().lower()
        version = str(item_meta.get("version", "")).strip()
        if not name:
            continue
        install_report[name] = item
        install_versions.setdefault(name, set())
        if version:
            install_versions[name].add(version)
        if bool(item.get("requested", False)):
            install_requested.add(name)
    expected_tags = set(sys_tags())
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
    if not install_report_path.exists():
        findings.append("missing_security_toolchain_install_report")
    allowed_names = {str(name).strip().lower() for name in lock if isinstance(name, str)}
    for tool_name, spec in transitive_lock.items():
        if not isinstance(tool_name, str) or not isinstance(spec, dict):
            continue
        allowed_names.add(tool_name.strip().lower())
        raw_transitive = spec.get("transitive", [])
        if isinstance(raw_transitive, list):
            for dep in raw_transitive:
                if isinstance(dep, str) and dep.strip():
                    allowed_names.add(dep.strip().lower())
    for observed_name in sorted(install_report):
        if observed_name not in allowed_names:
            findings.append(f"unexpected_dependency_install:{observed_name}")
    for observed_name, observed_versions in sorted(install_versions.items()):
        if len(observed_versions) > 1:
            findings.append(f"dependency_version_changed_during_install:{observed_name}:{','.join(sorted(observed_versions))}")
    for observed_name in sorted(install_requested):
        if observed_name not in {str(name).strip().lower() for name in lock if isinstance(name, str)}:
            findings.append(f"unexpected_requested_dependency:{observed_name}")
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
        install_item = install_report.get(package.lower(), {})
        if not isinstance(install_item, dict) or not install_item:
            findings.append(f"{package} missing install report entry")
        else:
            download = install_item.get("download_info", {})
            url = str(download.get("url", "")).strip() if isinstance(download, dict) else ""
            wheel_filename, wheel_tags = _wheel_tags_from_download_url(url)
            if not wheel_filename:
                findings.append(f"{package} missing wheel filename in download URL")
            elif not wheel_filename.endswith(".whl"):
                findings.append(f"{package} non-wheel distribution cannot verify ABI/platform tags")
            elif not wheel_tags:
                findings.append(f"{package} wheel tags unreadable")
            elif not (wheel_tags & expected_tags):
                findings.append(f"{package} wheel ABI/platform tags incompatible with interpreter")
            checks[package]["wheel_url"] = url or "missing"
            checks[package]["wheel_filename"] = wheel_filename or "missing"
            checks[package]["wheel_tag_match"] = bool(wheel_tags & expected_tags)
        if transitive_path.exists():
            transitive = transitive_lock.get(package, {})
            if not isinstance(transitive, dict) or not isinstance(transitive.get("transitive", []), list):
                findings.append(f"{package} missing transitive lock entry")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checks": checks,
        "summary": {
            "locked_packages": len(lock),
            "has_transitive_lock": transitive_path.exists(),
            "install_report_path": str(install_report_path),
            "expected_tag_sample": [str(tag) for tag in sorted(expected_tags, key=str)[:10]],
            "allowed_dependency_names": sorted(allowed_names),
        },
        "metadata": {"gate": "security_toolchain_gate"},
    }
    out = evidence_root() / "security" / "security_toolchain.json"
    write_json_report(out, payload)
    print(f"SECURITY_TOOLCHAIN_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
