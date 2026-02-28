#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import fixtures_root, goldens_root, vectors_root


def _check_manifests(root: Path, manifest_name: str) -> List[str]:
    errors: List[str] = []
    for manifest in root.rglob(manifest_name):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid json: {manifest} ({exc})")
            continue
        files = data.get("files", [])
        for entry in files:
            p = ROOT / entry.get("path", "")
            if not p.exists():
                errors.append(f"missing file: {p}")
    return errors


def _check_vectors_manifests(root: Path) -> List[str]:
    errors: List[str] = []
    for manifest in root.rglob("vectors-manifest.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid json: {manifest} ({exc})")
            continue
        vf = ROOT / data.get("vectors_file", "")
        if not vf.exists():
            errors.append(f"missing vectors file: {vf}")
    return errors


def main() -> int:
    errors: List[str] = []
    errors.extend(_check_manifests(fixtures_root(), "fixture-manifest.json"))
    errors.extend(_check_manifests(goldens_root(), "golden-manifest.json"))
    errors.extend(_check_vectors_manifests(vectors_root()))

    if errors:
        print("FIXTURE_GATE: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("FIXTURE_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
