#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tooling.codegen.generate import generate  # noqa: E402


def main() -> int:
    generate()
    proc = subprocess.run([sys.executable, "-m", "pytest"], check=False)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
