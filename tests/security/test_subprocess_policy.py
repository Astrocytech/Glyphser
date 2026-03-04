from __future__ import annotations

import sys

import pytest

from tooling.security.subprocess_policy import run_checked


def test_run_checked_allows_absolute_python_executable() -> None:
    proc = run_checked([sys.executable, "-c", "print('ok')"])
    assert proc.returncode == 0
    assert proc.stdout.strip() == "ok"


def test_run_checked_blocks_disallowed_commands() -> None:
    with pytest.raises(ValueError, match="subprocess command not allowed by policy"):
        run_checked(["/bin/echo", "nope"])
