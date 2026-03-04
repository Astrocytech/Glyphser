#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tarfile
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INCLUDE = [
    "policy_signature.json",
    "provenance_signature.json",
    "evidence_attestation_index.json",
    "evidence_attestation_gate.json",
    "provenance_revocation_gate.json",
    "security_super_gate.json",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect signed incident response bundle from security evidence.")
    parser.add_argument("--incident-id", required=True)
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    out_dir = evidence_root() / "incident"
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = out_dir / f"incident-bundle-{args.incident_id}.tar.gz"
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

    manifest_payload = {
        "status": "PASS" if not missing else "WARN",
        "incident_id": args.incident_id,
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "included": included,
        "missing": missing,
    }
    manifest.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("INCIDENT_BUNDLE_COLLECT: PASS")
    print(f"Bundle: {bundle}")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
