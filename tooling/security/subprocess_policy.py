from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT_SEC = 120.0
DEFAULT_MAX_OUTPUT_BYTES = 1_000_000

_ALLOWED_PREFIXES: list[tuple[str, ...]] = [
    ("git", "rev-parse"),
    ("git", "diff"),
    ("git", "log"),
    ("git", "ls-files"),
    ("java", "-version"),
    ("javac", "-version"),
    ("javac",),
    ("java", "-cp"),
    ("python",),
    ("python3",),
]
_PYTHON_INLINE_RE = re.compile(r"^[A-Za-z0-9_ .,:;()'\"=+-/*[\]{}<>!\\n\\t]+$")


def _allowed_python_args(cmd: list[str]) -> bool:
    if len(cmd) < 2:
        return False
    # Allow explicit pip module operations used by security tooling setup/verification.
    if len(cmd) >= 4 and cmd[1] == "-m" and cmd[2] == "pip" and cmd[3] in {"install", "freeze", "list"}:
        return True
    # Allow controlled one-liners used in tests and diagnostics.
    if len(cmd) == 3 and cmd[1] == "-c" and _PYTHON_INLINE_RE.fullmatch(cmd[2] or ""):
        return True
    # Allow executing repository-local python scripts.
    script = Path(cmd[1])
    if script.suffix != ".py":
        return False
    if script.is_absolute():
        return str(script).startswith(str(ROOT))
    return ".." not in script.parts


def _allowed_git_args(cmd: list[str]) -> bool:
    if len(cmd) < 2:
        return False
    subcmd = cmd[1]
    if subcmd == "rev-parse":
        return len(cmd) == 3 and cmd[2] == "HEAD"
    if subcmd == "ls-files":
        return len(cmd) >= 2
    if subcmd == "diff":
        return "--" in cmd
    if subcmd == "log":
        return "--" in cmd and "--pretty=%B" in cmd
    return False


def _allowed_java_args(cmd: list[str]) -> bool:
    return cmd[:2] == ["java", "-version"] or cmd[:2] == ["javac", "-version"]


def _allowed_java_exec_args(cmd: list[str]) -> bool:
    if cmd and cmd[0] == "javac":
        return len(cmd) >= 2 and all(not arg.startswith("-J") for arg in cmd[1:])
    if cmd[:2] == ["java", "-cp"]:
        return len(cmd) >= 4
    return False


def _allowed(cmd: list[str]) -> bool:
    exe_name = Path(cmd[0]).name.lower()
    if exe_name.startswith("python"):
        return _allowed_python_args(cmd)
    if exe_name == "git":
        return _allowed_git_args(cmd)
    if exe_name in {"java", "javac"}:
        return _allowed_java_args(cmd) or _allowed_java_exec_args(cmd)
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
    exit_reason: str = "exit"


async def _run_async(
    cmd: list[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None,
    timeout_sec: float,
    max_output_bytes: int,
) -> PolicyProcessResult:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        env=dict(env) if env is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
    except TimeoutError:
        proc.kill()
        stdout_b, stderr_b = await proc.communicate()
        return PolicyProcessResult(
            returncode=124,
            stdout=stdout_b[:max_output_bytes].decode("utf-8", errors="replace"),
            stderr=stderr_b[:max_output_bytes].decode("utf-8", errors="replace"),
            exit_reason="timeout",
        )
    truncated = len(stdout_b) > max_output_bytes or len(stderr_b) > max_output_bytes
    reason = "output_truncated" if truncated else "exit"
    return PolicyProcessResult(
        returncode=int(proc.returncode or 0),
        stdout=stdout_b[:max_output_bytes].decode("utf-8", errors="replace"),
        stderr=stderr_b[:max_output_bytes].decode("utf-8", errors="replace"),
        exit_reason=reason,
    )


def run_checked(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> PolicyProcessResult:
    if not cmd:
        raise ValueError("empty command")
    if not _allowed(cmd):
        raise ValueError(f"subprocess command not allowed by policy: {' '.join(cmd)}")
    if timeout_sec <= 0:
        raise ValueError("timeout_sec must be positive")
    if max_output_bytes <= 0:
        raise ValueError("max_output_bytes must be positive")
    return asyncio.run(
        _run_async(
            cmd,
            cwd=cwd or ROOT,
            env=env,
            timeout_sec=timeout_sec,
            max_output_bytes=max_output_bytes,
        )
    )
