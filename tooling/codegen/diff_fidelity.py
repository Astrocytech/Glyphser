#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_tmp_root

CLEAN = generated_tmp_root() / "codegen_staging" / "cleanroom_validation"

FILES = [
    "models.py",
    "operators.py",
    "validators.py",
    "error.py",
    "bindings.py",
]


def _sha256(path: Path) -> str:
    data = path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    missing = []
    drift = []
    for name in FILES:
        a = ROOT / "runtime" / "glyphser" / "_generated" / name
        b = CLEAN / name
        if not a.exists() or not b.exists():
            missing.append(name)
            continue
        if _sha256(a) != _sha256(b):
            drift.append(name)

    if missing or drift:
        print("CODEGEN_DIFF: FAIL")
        if missing:
            print(f"missing: {missing}")
        if drift:
            print(f"drift: {drift}")
        return 1

    print("CODEGEN_DIFF: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
