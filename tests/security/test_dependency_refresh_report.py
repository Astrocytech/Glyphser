from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tooling.security import dependency_refresh_report


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


def test_dependency_refresh_report_pass(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dependency_refresh_report, "_sp", _FakeRunner(0, stdout="[]"))
    monkeypatch.setattr(dependency_refresh_report, "evidence_root", lambda: tmp_path / "evidence")
    rc = dependency_refresh_report.main()
    assert rc == 0
    payload = json.loads((tmp_path / "evidence" / "security" / "dependency_outdated.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"


def test_dependency_refresh_report_fail(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dependency_refresh_report, "_sp", _FakeRunner(1, stdout="", stderr="pip failed"))
    monkeypatch.setattr(dependency_refresh_report, "evidence_root", lambda: tmp_path / "evidence")
    rc = dependency_refresh_report.main()
    assert rc == 1
    payload = json.loads((tmp_path / "evidence" / "security" / "dependency_outdated.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
