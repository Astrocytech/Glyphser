#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

MANIFEST = generated_root() / "metadata" / "codegen_manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not MANIFEST.exists():
        print("missing codegen_manifest.json; run codegen first")
        return 1

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    outputs = data.get("outputs", [])
    if not outputs:
        print("no outputs listed in codegen manifest")
        return 1

    missing = []
    drift = []
    for rel in outputs:
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        # recompute expected hash from content
        actual = _sha256(path)
        # allow manifest to be the source of truth if stored
        # otherwise we compute hash set from current outputs
        manifest_hashes = {entry.get("path"): entry.get("sha256") for entry in data.get("outputs_with_hashes", [])}
        if manifest_hashes:
            expected = manifest_hashes.get(rel)
            if expected and expected != actual:
                drift.append(rel)

    if missing or drift:
        print("GENERATED DRIFT: FAIL")
        if missing:
            print(f"missing outputs: {missing}")
        if drift:
            print(f"drifted outputs: {drift}")
        return 1

    print("GENERATED DRIFT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
