from __future__ import annotations

import sys

from tooling.security import install_security_toolchain


class _Proc:
    def __init__(self, code: int = 0) -> None:
        self.returncode = code
        self.stdout = ""
        self.stderr = ""


def test_install_security_toolchain_runs_pinned_install(monkeypatch) -> None:
    calls: list[list[str]] = []

    def _run_checked(cmd: list[str]):
        calls.append(cmd)
        return _Proc(0)

    monkeypatch.setattr(install_security_toolchain, "run_checked", _run_checked)
    assert install_security_toolchain.main([]) == 0
    assert calls[0] == [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    assert calls[1][:6] == [sys.executable, "-m", "pip", "install", "--upgrade", "bandit==1.9.4"]
    assert "setuptools==75.8.0" in calls[1]
