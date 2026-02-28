#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tooling"))
from path_config import generated_root

OUT = generated_root() / "input_hashes.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    inputs = []
    for path in sorted((ROOT / "schemas").rglob("*.schema.json")):
        inputs.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256(path)})
    reg = ROOT / "specs" / "contracts" / "operator_registry.json"
    if reg.exists():
        inputs.append({"path": str(reg.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256(reg)})
    for path in sorted((ROOT / "tooling" / "codegen" / "templates").glob("*.tpl")):
        inputs.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256(path)})

    OUT.write_text(json.dumps({"inputs": inputs}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
