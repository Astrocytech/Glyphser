from __future__ import annotations

import sys

import pytest

from tooling.security.subprocess_policy import run_checked


def test_run_checked_allows_absolute_python_executable() -> None:
    proc = run_checked([sys.executable, "-c", "print('ok')"])
    assert proc.returncode == 0
    assert proc.stdout.strip() == "ok"
    assert proc.exit_reason == "exit"


def test_run_checked_blocks_disallowed_commands() -> None:
    with pytest.raises(ValueError, match="subprocess command not allowed by policy"):
        run_checked(["/bin/echo", "nope"])


def test_run_checked_blocks_disallowed_python_invocation() -> None:
    with pytest.raises(ValueError, match="subprocess command not allowed by policy"):
        run_checked([sys.executable, "-m", "http.server"])


def test_run_checked_blocks_unconstrained_git_diff() -> None:
    with pytest.raises(ValueError, match="subprocess command not allowed by policy"):
        run_checked(["git", "diff", "HEAD~1", "HEAD"])


def test_run_checked_enforces_timeout() -> None:
    proc = run_checked(
        [sys.executable, "-c", "import time; time.sleep(0.2)"],
        timeout_sec=0.01,
    )
    assert proc.returncode == 124
    assert proc.exit_reason == "timeout"


def test_run_checked_truncates_large_output() -> None:
    proc = run_checked(
        [sys.executable, "-c", "print('x' * 2000)"],
        max_output_bytes=256,
    )
    assert proc.returncode == 0
    assert proc.exit_reason == "output_truncated"
    assert len(proc.stdout.encode('utf-8')) <= 256
