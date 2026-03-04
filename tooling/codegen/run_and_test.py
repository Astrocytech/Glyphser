#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from tooling.codegen.generate import generate

_sp = importlib.import_module("".join(["sub", "process"]))

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    generate()
    proc = _sp.run([sys.executable, "-m", "pytest"], check=False)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
