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

INSTALL_REPORT = ROOT / "evidence" / "security" / "security_toolchain_install_report.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _extract_rows(payload: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    installs = payload.get("install", []) if isinstance(payload, dict) else []
    if not isinstance(installs, list):
        installs = []

    for item in installs:
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata", {})
        name = str(meta.get("name", "")).strip().lower() if isinstance(meta, dict) else ""
        version = str(meta.get("version", "")).strip() if isinstance(meta, dict) else ""
        download = item.get("download_info", {}) if isinstance(item.get("download_info", {}), dict) else {}
        url = str(download.get("url", "")).strip()
        archive = download.get("archive_info", {}) if isinstance(download.get("archive_info", {}), dict) else {}

        sha = ""
        hashes = archive.get("hashes", {}) if isinstance(archive.get("hashes", {}), dict) else {}
        if isinstance(hashes, dict):
            sha = str(hashes.get("sha256", "")).strip().lower()
        if not sha:
            fallback = str(archive.get("hash", "")).strip().lower()
            if fallback.startswith("sha256="):
                sha = fallback.split("=", 1)[1]

        if name and version and sha:
            out.append({"name": name, "version": version, "sha256": sha, "url": url})
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not INSTALL_REPORT.exists():
        findings.append("missing_security_toolchain_install_report")
        rows: list[dict[str, str]] = []
    else:
        rows = _extract_rows(_load_json(INSTALL_REPORT))

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = f"{row['name']}=={row['version']}"
        grouped.setdefault(key, []).append(row)

    comparisons: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items()):
        hashes = sorted({item["sha256"] for item in items})
        urls = sorted({item["url"] for item in items if item["url"]})
        comparison = {
            "package": key,
            "unique_hashes": [f"sha256:{h}" for h in hashes],
            "source_urls": urls,
            "source_count": len(urls),
            "consistent": len(hashes) <= 1,
        }
        comparisons.append(comparison)
        if len(hashes) > 1:
            findings.append(f"mirrored_source_hash_mismatch:{key}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "packages_compared": len(comparisons),
            "mismatch_packages": len([item for item in comparisons if not item["consistent"]]),
        },
        "metadata": {"gate": "mirrored_source_integrity_report"},
        "comparisons": comparisons,
    }
    out = evidence_root() / "security" / "mirrored_source_integrity_report.json"
    write_json_report(out, report)
    print(f"MIRRORED_SOURCE_INTEGRITY_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
