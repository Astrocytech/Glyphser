#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

OUT = generated_root() / "deploy" / "env_manifest.json"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate() -> Path:
    payload = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"env": payload, "env_hash": _sha256_hex(text.encode("utf-8"))}, indent=2, sort_keys=True) + "\n")
    return OUT


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
