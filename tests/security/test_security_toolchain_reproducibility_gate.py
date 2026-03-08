from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_toolchain_reproducibility_gate


class _Proc:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ""


def test_security_toolchain_reproducibility_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "security_toolchain_lock.json").write_text(
        json.dumps({"bandit": {"version": "1.9.4"}, "semgrep": {"version": "1.95.0"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_toolchain_reproducibility_gate, "ROOT", repo)
    monkeypatch.setattr(security_toolchain_reproducibility_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        security_toolchain_reproducibility_gate,
        "run_checked",
        lambda *_a, **_k: _Proc("bandit==1.9.4\nsemgrep==1.95.0\n"),
    )
    assert security_toolchain_reproducibility_gate.main([]) == 0


def test_security_toolchain_reproducibility_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "security_toolchain_lock.json").write_text(
        json.dumps({"bandit": {"version": "1.9.4"}, "semgrep": {"version": "1.95.0"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_toolchain_reproducibility_gate, "ROOT", repo)
    monkeypatch.setattr(security_toolchain_reproducibility_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        security_toolchain_reproducibility_gate,
        "run_checked",
        lambda *_a, **_k: _Proc("bandit==1.9.4\nsemgrep==1.96.0\n"),
    )
    assert security_toolchain_reproducibility_gate.main([]) == 1
    payload = json.loads(
        (repo / "evidence" / "security" / "security_toolchain_reproducibility_gate.json").read_text("utf-8")
    )
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("toolchain_version_mismatch:") for item in payload["findings"])
