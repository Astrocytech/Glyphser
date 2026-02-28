#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.path_config import fixtures_root, goldens_root, vectors_root


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    for rel, info in m.get("artifacts", {}).items():
        p = manifest_path.parent / rel
        if not p.exists():
            errors.append(f"missing artifact: {p}")
            continue
        h = sha256_hex(p)
        if h != info.get("sha256"):
            errors.append(f"hash mismatch: {p} expected={info.get('sha256')} got={h}")
        if p.stat().st_size != info.get("size_bytes"):
            errors.append(f"size mismatch: {p} expected={info.get('size_bytes')} got={p.stat().st_size}")
    return errors


def verify_file_list_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in m.get("files", []):
        p = ROOT / entry["path"]
        if not p.exists():
            errors.append(f"missing file: {p}")
            continue
        h = sha256_hex(p)
        if h != entry.get("sha256"):
            errors.append(f"hash mismatch: {p} expected={entry.get('sha256')} got={h}")
        if p.stat().st_size != entry.get("size_bytes"):
            errors.append(f"size mismatch: {p} expected={entry.get('size_bytes')} got={p.stat().st_size}")
    return errors


def main() -> int:
    checks = [
        (ROOT / "specs" / "contracts" / "catalog-manifest.json", verify_manifest),
    ]

    for path in fixtures_root().rglob("fixture-manifest.json"):
        checks.append((path, verify_file_list_manifest))

    for path in goldens_root().rglob("golden-manifest.json"):
        checks.append((path, verify_file_list_manifest))

    all_errors: list[str] = []
    for path, fn in checks:
        if not path.exists():
            all_errors.append(f"missing manifest: {path}")
            continue
        errs = fn(path)
        all_errors.extend(errs)

    for vmanifest in vectors_root().rglob("vectors-manifest.json"):
        vm = json.loads(vmanifest.read_text(encoding="utf-8"))
        vf = ROOT / vm["vectors_file"]
        if not vf.exists():
            all_errors.append(f"missing vectors file: {vf}")
        else:
            h = sha256_hex(vf)
            if h != vm.get("vectors_file_sha256"):
                all_errors.append(
                    f"vectors hash mismatch: expected={vm.get('vectors_file_sha256')} got={h}"
                )

    if all_errors:
        print("VERIFY_DOC_ARTIFACTS: FAIL")
        for e in all_errors:
            print(f" - {e}")
        return 1

    print("VERIFY_DOC_ARTIFACTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
