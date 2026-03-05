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

POLICY_PATH = ROOT / "governance" / "security" / "dependency_registry_policy.json"
LOCK_PATH = ROOT / "requirements.lock"
REQ_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_lock(lock_path: Path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if not lock_path.exists():
        return out
    for raw in lock_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("--"):
            continue
        m = REQ_RE.match(line)
        if not m:
            continue
        out.append((m.group(1).lower(), m.group(2)))
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY_PATH) if POLICY_PATH.exists() else {}
    forbidden_maintainers = {
        str(item).strip().lower() for item in policy.get("forbidden_maintainers", []) if isinstance(item, str)
    }
    fail_on_missing_snapshot = bool(policy.get("fail_on_missing_snapshot", True))
    fail_on_missing_package_metadata = bool(policy.get("fail_on_missing_package_metadata", False))
    snapshot_rel = str(policy.get("registry_snapshot_path", "governance/security/metadata/dependency_registry_snapshot.json"))
    snapshot_path = ROOT / snapshot_rel

    findings: list[str] = []
    if not snapshot_path.exists():
        if fail_on_missing_snapshot:
            findings.append("missing_registry_snapshot")
        snapshot: dict[str, Any] = {}
    else:
        snapshot = _load_json(snapshot_path)
    packages = snapshot.get("packages", {}) if isinstance(snapshot, dict) else {}
    if not isinstance(packages, dict):
        packages = {}

    checked = 0
    missing_meta = 0
    yanked_hits = 0
    maintainer_hits = 0
    for package, version in _parse_lock(LOCK_PATH):
        checked += 1
        meta = packages.get(package)
        if not isinstance(meta, dict):
            missing_meta += 1
            if fail_on_missing_package_metadata:
                findings.append(f"missing_package_metadata:{package}:{version}")
            continue

        maintainers = {
            str(item).strip().lower() for item in meta.get("maintainers", []) if isinstance(item, str) and str(item).strip()
        }
        yanked = {str(item).strip() for item in meta.get("yanked_versions", []) if isinstance(item, str) and str(item).strip()}

        for owner in sorted(maintainers):
            if owner in forbidden_maintainers:
                maintainer_hits += 1
                findings.append(f"forbidden_maintainer:{package}:{owner}")
        if version in yanked:
            yanked_hits += 1
            findings.append(f"yanked_version:{package}:{version}")

    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "checked_packages": checked,
            "missing_package_metadata": missing_meta,
            "forbidden_maintainer_hits": maintainer_hits,
            "yanked_version_hits": yanked_hits,
            "forbidden_maintainers": sorted(forbidden_maintainers),
            "registry_snapshot_path": str(snapshot_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "dependency_registry_policy_gate"},
    }
    out = evidence_root() / "security" / "dependency_registry_policy_gate.json"
    write_json_report(out, report)
    print(f"DEPENDENCY_REGISTRY_POLICY_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
