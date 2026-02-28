#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import gzip
import tarfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tooling"))
from path_config import (
    bundles_root,
    conformance_reports_root,
    conformance_results_root,
    fixtures_root,
    goldens_root,
    first_existing,
    rel,
)

DIST = bundles_root()


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iter_bundle_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_file():
            out.append(p)
            continue
        for child in sorted(p.rglob("*")):
            if child.is_file():
                out.append(child)
    return out


def _normalized_tarinfo(tf: tarfile.TarFile, path: Path, arcname: str) -> tarfile.TarInfo:
    info = tf.gettarinfo(str(path), arcname=arcname)
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    info.mode = 0o755 if (info.mode & 0o111) else 0o644
    return info


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    bundle = DIST / "hello-core-bundle.tar.gz"

    paths = [
        ROOT / "contracts" / "catalog-manifest.json",
        ROOT / "contracts" / "operator_registry.cbor",
        ROOT / "contracts" / "operator_registry.json",
        ROOT / "contracts" / "interface_hash.json",
        fixtures_root() / "hello-core",
        goldens_root() / "hello-core",
        conformance_results_root() / "latest.json",
        conformance_reports_root() / "latest.json",
        first_existing([rel("docs", "VERIFY.md"), rel("product", "docs", "VERIFY.md")]),
    ]

    files = _iter_bundle_files(paths)
    with bundle.open("wb") as raw:
        # Fix gzip timestamp/header for cross-host reproducibility.
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tf:
                for p in files:
                    arcname = p.relative_to(ROOT).as_posix()
                    info = _normalized_tarinfo(tf, p, arcname)
                    with p.open("rb") as fh:
                        tf.addfile(info, fh)

    manifest = DIST / "hello-core-bundle.sha256"
    manifest.write_text(f"{sha256_hex(bundle)}  {bundle.name}\n", encoding="utf-8")

    print(f"bundle: {bundle}")
    print(f"manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
