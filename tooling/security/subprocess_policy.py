from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]

_ALLOWED_PREFIXES: list[tuple[str, ...]] = [
    ("git", "rev-parse"),
    ("git", "ls-files"),
    ("java", "-version"),
    ("javac", "-version"),
    ("javac",),
    ("java", "-cp"),
    ("python",),
    ("python3",),
]


def _allowed(cmd: list[str]) -> bool:
    parts = tuple(cmd)
    for prefix in _ALLOWED_PREFIXES:
        if parts[: len(prefix)] == prefix:
            return True
    return False


def run_checked(cmd: list[str], *, cwd: Path | None = None, capture_output: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    if not cmd:
        raise ValueError("empty command")
    if not _allowed(cmd):
        raise ValueError(f"subprocess command not allowed by policy: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(cwd or ROOT), check=False, capture_output=capture_output, text=text)
