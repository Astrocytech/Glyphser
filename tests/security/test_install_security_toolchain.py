from __future__ import annotations

import json
import sys
from pathlib import Path

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

    repo = Path.cwd()
    lock = repo / "tooling" / "security" / "security_toolchain_lock.json"
    constraints = repo / "tooling" / "security" / "security_toolchain_constraints.txt"
    monkeypatch.setattr(install_security_toolchain, "LOCK_PATH", lock)
    monkeypatch.setattr(install_security_toolchain, "CONSTRAINTS_PATH", constraints)
    monkeypatch.setattr(install_security_toolchain, "run_checked", _run_checked)
    assert install_security_toolchain.main([]) == 0
    assert calls[0] == [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    assert calls[1][:7] == [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(constraints)]


def test_install_security_toolchain_fails_on_lock_constraints_mismatch(monkeypatch, tmp_path: Path) -> None:
    sec = tmp_path / "tooling" / "security"
    sec.mkdir(parents=True)
    lock = sec / "security_toolchain_lock.json"
    constraints = sec / "security_toolchain_constraints.txt"
    lock.write_text(
        json.dumps({"bandit": {"version": "1.9.4"}, "semgrep": {"version": "1.95.0"}}) + "\n",
        encoding="utf-8",
    )
    constraints.write_text("bandit==1.9.4\nsemgrep==1.96.0\n", encoding="utf-8")
    monkeypatch.setattr(install_security_toolchain, "LOCK_PATH", lock)
    monkeypatch.setattr(install_security_toolchain, "CONSTRAINTS_PATH", constraints)
    try:
        install_security_toolchain.main([])
    except ValueError as exc:
        assert "constraints mismatch lock" in str(exc)
    else:
        raise AssertionError("expected ValueError for lock/constraints mismatch")
