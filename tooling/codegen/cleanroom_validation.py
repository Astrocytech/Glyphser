#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from tooling.lib.path_config import generated_tmp_root

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
CLEAN = generated_tmp_root() / "codegen_staging" / "cleanroom_validation"


def main() -> int:
    if CLEAN.exists():
        shutil.rmtree(CLEAN)
    CLEAN.mkdir(parents=True, exist_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
