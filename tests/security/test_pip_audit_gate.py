from __future__ import annotations

import json
from pathlib import Path

from tooling.security import pip_audit_gate


class _FakeRunner:
    def __init__(self, rc: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr
        self.calls: list[dict[str, object]] = []

    def __call__(self, cmd: list[str], **kwargs):
        self.calls.append({"cmd": cmd, **kwargs})
        return self


class _FakePathConfig:
    def __init__(self, root: Path) -> None:
        self._root = root

    def evidence_root(self) -> Path:
        return self._root


def test_pip_audit_gate_writes_pass_report(monkeypatch, tmp_path: Path):
    runner = _FakeRunner(0, stdout="[]", stderr="")
    monkeypatch.setattr(pip_audit_gate, "run_checked", runner)

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
    assert payload["summary"]["resource_budget"]["timeout_sec"] == pip_audit_gate.DEFAULT_TIMEOUT_SEC


def test_pip_audit_gate_writes_fail_report(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pip_audit_gate, "run_checked", _FakeRunner(1, stdout="", stderr="vuln"))

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


def test_pip_audit_gate_applies_resource_budget_overrides(monkeypatch, tmp_path: Path):
    runner = _FakeRunner(0, stdout="[]", stderr="")
    monkeypatch.setattr(pip_audit_gate, "run_checked", runner)
    monkeypatch.setenv("GLYPHSER_PIP_AUDIT_TIMEOUT_SEC", "42")
    monkeypatch.setenv("GLYPHSER_PIP_AUDIT_MAX_OUTPUT_BYTES", "777")

    def _fake_import(name: str):
        if name == "tooling.lib.path_config":
            return _FakePathConfig(tmp_path / "evidence")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(pip_audit_gate.importlib, "import_module", _fake_import)
    assert pip_audit_gate.main([]) == 0
    assert runner.calls
    assert runner.calls[0]["timeout_sec"] == 42.0
    assert runner.calls[0]["max_output_bytes"] == 777
