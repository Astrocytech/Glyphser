from __future__ import annotations

import json
from pathlib import Path

from tooling.security import locale_variance_suite


class _Proc:
    def __init__(self, rc: int = 0) -> None:
        self.returncode = rc
        self.stdout = ""
        self.stderr = ""


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_locale_variance_suite_passes_when_reports_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    def _run_checked(cmd, *, cwd, env):
        _ = cwd
        script = cmd[1]
        report = locale_variance_suite.TARGET_GATES[[item[0] for item in locale_variance_suite.TARGET_GATES].index(script)][1]
        run_root = Path(env["GLYPHSER_EVIDENCE_ROOT"])
        _write_json(run_root / "security" / report, {"status": "PASS", "findings": ["stable"]})
        return _Proc(0)

    monkeypatch.setattr(locale_variance_suite, "ROOT", repo)
    monkeypatch.setattr(locale_variance_suite, "evidence_root", lambda: ev)
    monkeypatch.setattr(locale_variance_suite, "run_checked", _run_checked)

    assert locale_variance_suite.main([]) == 0
    report = json.loads((ev / "security" / "locale_variance_suite.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_locale_variance_suite_fails_on_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    def _run_checked(cmd, *, cwd, env):
        _ = cwd
        script = cmd[1]
        report = locale_variance_suite.TARGET_GATES[[item[0] for item in locale_variance_suite.TARGET_GATES].index(script)][1]
        run_root = Path(env["GLYPHSER_EVIDENCE_ROOT"])
        finding = "alpha" if env["LC_ALL"] == "C.UTF-8" else "beta"
        _write_json(run_root / "security" / report, {"status": "PASS", "findings": [finding]})
        return _Proc(0)

    monkeypatch.setattr(locale_variance_suite, "ROOT", repo)
    monkeypatch.setattr(locale_variance_suite, "evidence_root", lambda: ev)
    monkeypatch.setattr(locale_variance_suite, "run_checked", _run_checked)

    assert locale_variance_suite.main([]) == 1
    report = json.loads((ev / "security" / "locale_variance_suite.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("locale_behavior_drift:") for item in report["findings"])
