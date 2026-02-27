#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main() -> int:
    meta = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
        "cpu": platform.processor() or platform.machine(),
    }
    lock = ROOT / "requirements.lock"
    if lock.exists():
        meta["dependency_lock"] = "requirements.lock"
    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
