#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    bundle = DIST / "hello-core-bundle.tar.gz"

    paths = [
        ROOT / "contracts" / "catalog-manifest.json",
        ROOT / "contracts" / "operator_registry.cbor",
        ROOT / "contracts" / "operator_registry.json",
        ROOT / "contracts" / "interface_hash.json",
        ROOT / "fixtures" / "hello-core",
        ROOT / "goldens" / "hello-core",
        ROOT / "conformance" / "results" / "latest.json",
        ROOT / "conformance" / "reports" / "latest.json",
        ROOT / "docs" / "VERIFY.md",
    ]

    with tarfile.open(bundle, "w:gz") as tf:
        for p in paths:
            if not p.exists():
                continue
            tf.add(p, arcname=p.relative_to(ROOT))

    manifest = DIST / "hello-core-bundle.sha256"
    manifest.write_text(f"{sha256_hex(bundle)}  {bundle.name}\n", encoding="utf-8")

    print(f"bundle: {bundle}")
    print(f"manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
