from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]

_ALLOWED_PREFIXES: list[tuple[str, ...]] = [
    ("git", "rev-parse"),
    ("git", "diff"),
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


@dataclass(frozen=True)
class PolicyProcessResult:
    returncode: int
    stdout: str
    stderr: str


async def _run_async(cmd: list[str], *, cwd: Path, env: Mapping[str, str] | None) -> PolicyProcessResult:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        env=dict(env) if env is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_b, stderr_b = await proc.communicate()
    return PolicyProcessResult(
        returncode=int(proc.returncode or 0),
        stdout=stdout_b.decode("utf-8", errors="replace"),
        stderr=stderr_b.decode("utf-8", errors="replace"),
    )


def run_checked(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> PolicyProcessResult:
    if not cmd:
        raise ValueError("empty command")
    if not _allowed(cmd):
        raise ValueError(f"subprocess command not allowed by policy: {' '.join(cmd)}")
    return asyncio.run(_run_async(cmd, cwd=cwd or ROOT, env=env))
