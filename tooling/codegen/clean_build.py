#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tooling"))
from path_config import generated_root

CLEAN = generated_root() / "clean_build"


def main() -> int:
    if CLEAN.exists():
        shutil.rmtree(CLEAN)
    CLEAN.mkdir(parents=True, exist_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
