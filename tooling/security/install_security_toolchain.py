#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys

run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked

PINNED_PACKAGES = [
    "bandit==1.9.4",
    "pip-audit==2.9.0",
    "semgrep==1.95.0",
    "setuptools==75.8.0",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cmds = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "--upgrade", *PINNED_PACKAGES],
    ]
    for cmd in cmds:
        proc = run_checked(cmd)
        if proc.returncode != 0:
            print(proc.stdout, end="")
            print(proc.stderr, end="", file=sys.stderr)
            return int(proc.returncode)
    print("SECURITY_TOOLCHAIN_INSTALL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
