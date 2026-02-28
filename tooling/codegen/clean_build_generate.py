#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tooling"))

from tooling.codegen.clean_build import main as clean_build  # noqa: E402
from tooling.codegen.generate import generate  # noqa: E402
from path_config import generated_root  # noqa: E402

CLEAN = generated_root() / "codegen" / "clean_build"


def main() -> int:
    clean_build()
    generate()

    # copy generated outputs into clean_build
    outputs = json.loads(
        (generated_root() / "build_metadata" / "codegen_manifest.json").read_text(encoding="utf-8")
    )["outputs"]
    for rel in outputs:
        src = ROOT / rel
        dst = CLEAN / Path(rel).name
        shutil.copy2(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
