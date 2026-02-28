#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
IN_DIR = ROOT / "tooling" / "deploy" / "overlay_templates"
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

OUT_DIR = generated_root() / "deploy" / "overlays"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = {"profiles": []}
    for profile in ("dev", "staging", "prod"):
        src = IN_DIR / f"{profile}.json"
        dst = OUT_DIR / f"{profile}.json"
        if not src.exists():
            print(f"missing overlay source: {src}")
            return 1
        payload = json.loads(src.read_text(encoding="utf-8"))
        dst.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        index["profiles"].append(
            {
                "profile": profile,
                "path": str(dst.relative_to(ROOT)).replace("\\", "/"),
                "sha256": _sha256(dst),
            }
        )
    (OUT_DIR / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
