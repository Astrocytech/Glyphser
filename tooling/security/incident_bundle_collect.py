#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import tarfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
DEFAULT_INCLUDE = [
    "policy_signature.json",
    "provenance_signature.json",
    "evidence_attestation_index.json",
    "evidence_attestation_gate.json",
    "provenance_revocation_gate.json",
    "security_super_gate.json",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect signed incident response bundle from security evidence.")
    parser.add_argument("--incident-id", required=True)
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    out_dir = evidence_root() / "incident"
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = out_dir / f"incident-bundle-{args.incident_id}.tar.gz"
    bundle_sha = out_dir / f"incident-bundle-{args.incident_id}.tar.gz.sha256"
    manifest = out_dir / f"incident-bundle-{args.incident_id}.manifest.json"

    included: list[str] = []
    missing: list[str] = []
    with tarfile.open(bundle, "w:gz") as tf:
        for name in DEFAULT_INCLUDE:
            path = sec / name
            if path.exists():
                tf.add(path, arcname=f"security/{name}")
                included.append(name)
            else:
                missing.append(name)
            sig = path.with_suffix(path.suffix + ".sig")
            if sig.exists():
                tf.add(sig, arcname=f"security/{sig.name}")
                included.append(sig.name)

    digest = _sha256(bundle)
    bundle_sha.write_text(f"{digest}  {bundle.name}\n", encoding="utf-8")

    manifest_payload = {
        "status": "PASS" if not missing else "WARN",
        "incident_id": args.incident_id,
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "bundle_sha256": digest,
        "bundle_sha256_path": str(bundle_sha.relative_to(ROOT)).replace("\\", "/"),
        "included": included,
        "missing": missing,
    }
    write_json_report(manifest, manifest_payload)
    print("INCIDENT_BUNDLE_COLLECT: PASS")
    print(f"Bundle: {bundle}")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
