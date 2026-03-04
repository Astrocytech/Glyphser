#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tooling.codegen.cleanroom_validation import main as clean_build
from tooling.codegen.generate import generate
from tooling.lib.path_config import generated_root, generated_tmp_root

ROOT = Path(__file__).resolve().parents[2]


CLEAN = generated_tmp_root() / "codegen_staging" / "cleanroom_validation"


def _norm_sha256(path: Path) -> str:
    data = path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    clean_build()
    generate()

    # Persist a cleanroom hash snapshot; do not persist duplicate generated modules.
    outputs = json.loads((generated_root() / "metadata" / "codegen_manifest.json").read_text(encoding="utf-8"))[
        "outputs"
    ]
    snapshot = {
        "source_manifest": "artifacts/generated/stable/metadata/codegen_manifest.json",
        "hashes": {Path(rel).name: _norm_sha256(ROOT / rel) for rel in outputs},
    }
    (CLEAN / "hashes.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
