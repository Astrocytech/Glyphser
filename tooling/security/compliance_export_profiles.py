#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "compliance_export_profiles.json"
CLASSIFICATION_MANIFEST = ROOT / "governance" / "security" / "artifact_classification_manifest.json"


def _load_policy() -> dict[str, object]:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid compliance export policy")
    return payload


def _classification_map() -> dict[str, str]:
    if not CLASSIFICATION_MANIFEST.exists():
        return {}
    payload = json.loads(CLASSIFICATION_MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("artifacts", []) if isinstance(payload, dict) else []
    out: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        rel = str(row.get("path", "")).strip()
        classification = str(row.get("classification", "")).strip()
        if rel and classification:
            out[rel] = classification
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build signed compliance export bundles from filtered security artifacts.")
    parser.add_argument("--profile", required=True, help="Compliance profile name (for example: soc2_like, iso_like).")
    parser.add_argument("--strict-key", action="store_true", help="Require strict signing key for manifest signature.")
    args = parser.parse_args([] if argv is None else argv)

    policy = _load_policy()
    classifications = _classification_map()
    profiles = policy.get("profiles", {}) if isinstance(policy.get("profiles"), dict) else {}
    profile = str(args.profile).strip()
    entry = profiles.get(profile)
    findings: list[str] = []
    copied: list[str] = []
    labeled: list[dict[str, str]] = []

    if not isinstance(entry, dict):
        findings.append(f"unknown_profile:{profile}")
        entry = {}

    raw_artifacts = entry.get("artifacts", []) if isinstance(entry.get("artifacts"), list) else []
    artifacts = [str(item).strip() for item in raw_artifacts if isinstance(item, str) and str(item).strip()]

    export_root = evidence_root() / "security" / "compliance_exports" / profile
    export_root.mkdir(parents=True, exist_ok=True)

    for rel in artifacts:
        src = ROOT / rel
        if not src.exists() or not src.is_file():
            findings.append(f"missing_artifact:{rel}")
            continue
        dst = export_root / rel.replace("/", "__")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)
        label = classifications.get(rel, "")
        if not label:
            findings.append(f"missing_artifact_classification_label:{rel}")
        else:
            labeled.append({"artifact": rel, "classification": label})

    manifest = {
        "schema_version": 1,
        "profile": profile,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "copied_artifacts": copied,
    }
    manifest_path = export_root / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (export_root / "classification_labels.json").write_text(
        json.dumps({"labels": labeled}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    sig = artifact_signing.sign_file(manifest_path, key=artifact_signing.current_key(strict=args.strict_key))
    manifest_path.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "profile": profile,
            "requested_artifacts": len(artifacts),
            "copied_artifacts": len(copied),
            "classified_artifacts": len(labeled),
            "bundle_dir": str(export_root.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "compliance_export_profiles"},
    }
    out = evidence_root() / "security" / "compliance_export_profiles.json"
    write_json_report(out, report)
    print(f"COMPLIANCE_EXPORT_PROFILES: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
