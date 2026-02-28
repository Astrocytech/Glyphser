#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tooling.codegen.cleanroom_validation import main as clean_build  # noqa: E402
from tooling.codegen.generate import generate  # noqa: E402
from tooling.lib.path_config import generated_root  # noqa: E402

CLEAN = generated_root() / "codegen_staging" / "cleanroom_validation"


def main() -> int:
    clean_build()
    generate()

    # copy generated outputs into cleanroom validation directory
    outputs = json.loads(
        (generated_root() / "metadata" / "codegen_manifest.json").read_text(encoding="utf-8")
    )["outputs"]
    for rel in outputs:
        src = ROOT / rel
        dst = CLEAN / Path(rel).name
        shutil.copy2(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
