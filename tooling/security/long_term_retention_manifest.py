#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "security_retention_policy.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _read_sidecar_digest(sidecar: Path) -> str:
    line = sidecar.read_text(encoding="utf-8").strip()
    if not line:
        return ""
    return line.split()[0].strip().lower()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    policy: dict[str, Any] = {}
    if not POLICY.exists():
        findings.append("missing_security_retention_policy")
    else:
        raw = json.loads(POLICY.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            policy = raw
        else:
            findings.append("invalid_security_retention_policy")

    storage_location = str(policy.get("storage_location", "")).strip()
    retention_class = str(policy.get("retention_class", "")).strip()
    if not storage_location:
        findings.append("missing_storage_location")
    if not retention_class:
        findings.append("missing_retention_class")

    ev = evidence_root()
    entries: list[dict[str, str]] = []
    for bundle in sorted(ev.rglob("*.tar.gz")):
        rel = str(bundle.relative_to(ROOT)).replace("\\", "/")
        sidecar = bundle.with_name(bundle.name + ".sha256")
        if not sidecar.exists():
            findings.append(f"missing_bundle_digest:{rel}")
            continue
        sidecar_digest = _read_sidecar_digest(sidecar)
        if not sidecar_digest:
            findings.append(f"invalid_bundle_digest_sidecar:{rel}")
            continue
        actual = _sha256(bundle)
        if sidecar_digest != actual:
            findings.append(f"bundle_digest_mismatch:{rel}")
            continue
        entries.append(
            {
                "path": rel,
                "sha256": actual,
                "digest": f"sha256:{actual}",
                "storage_location": storage_location,
            }
        )

    material = {
        "storage_location": storage_location,
        "retention_class": retention_class,
        "entries": entries,
    }
    immutable = hashlib.sha256(_canonical(material).encode("utf-8")).hexdigest()
    report = {
        "status": "PASS" if not findings else "FAIL",
        "generated_at": datetime.now(UTC).isoformat(),
        "findings": findings,
        "summary": {
            "storage_location": storage_location,
            "retention_class": retention_class,
            "bundle_count": len(entries),
            "immutable_manifest_digest": f"sha256:{immutable}",
        },
        "entries": entries,
        "metadata": {"gate": "long_term_retention_manifest", "network_access": "not_required"},
    }
    out = ev / "security" / "long_term_retention_manifest.json"
    write_json_report(out, report)
    print(f"LONG_TERM_RETENTION_MANIFEST: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
