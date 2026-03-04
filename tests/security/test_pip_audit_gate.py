from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tooling.security import pip_audit_gate


class _FakeProc(SimpleNamespace):
    pass


class _FakeRunner:
    def __init__(self, rc: int, stdout: str = "", stderr: str = "") -> None:
        self._proc = _FakeProc(returncode=rc, stdout=stdout, stderr=stderr)

    def run(self, *_args, **_kwargs):
        return self._proc


class _FakePathConfig:
    def __init__(self, root: Path) -> None:
        self._root = root

    def evidence_root(self) -> Path:
        return self._root


def test_pip_audit_gate_writes_pass_report(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pip_audit_gate, "_sp", _FakeRunner(0, stdout="[]", stderr=""))

    def _fake_import(name: str):
        if name == "tooling.lib.path_config":
            return _FakePathConfig(tmp_path / "evidence")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(pip_audit_gate.importlib, "import_module", _fake_import)

    rc = pip_audit_gate.main()
    assert rc == 0

    report = tmp_path / "evidence" / "security" / "pip_audit.json"
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["returncode"] == 0


def test_pip_audit_gate_writes_fail_report(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pip_audit_gate, "_sp", _FakeRunner(1, stdout="", stderr="vuln"))

    def _fake_import(name: str):
        if name == "tooling.lib.path_config":
            return _FakePathConfig(tmp_path / "evidence")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(pip_audit_gate.importlib, "import_module", _fake_import)

    rc = pip_audit_gate.main()
    assert rc == 0

    report = tmp_path / "evidence" / "security" / "pip_audit.json"
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "WARN"
    assert payload["returncode"] == 1
