#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from path_config import bundles_root, evidence_root

OUT = evidence_root() / "repro" / "hashes.txt"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    target = bundles_root() / "hello-core-bundle.tar.gz"
    if not target.exists():
        print("missing bundle to hash")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    line = f"{_sha256(target)}  {target.name}\n"
    OUT.write_text(line, encoding="utf-8")
    print("REPRODUCIBILITY: wrote hash snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
