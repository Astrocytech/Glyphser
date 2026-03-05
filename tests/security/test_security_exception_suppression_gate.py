from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_exception_suppression_gate


def test_security_exception_suppression_gate_passes_without_suppression(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "ok.py").write_text(
        "def f():\n    try:\n        return 1\n    except ValueError:\n        return 0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_exception_suppression_gate, "ROOT", repo)
    monkeypatch.setattr(security_exception_suppression_gate, "evidence_root", lambda: repo / "evidence")
    assert security_exception_suppression_gate.main([]) == 0


def test_security_exception_suppression_gate_fails_on_broad_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "bad.py").write_text(
        "def f():\n    try:\n        return 1\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_exception_suppression_gate, "ROOT", repo)
    monkeypatch.setattr(security_exception_suppression_gate, "evidence_root", lambda: repo / "evidence")
    assert security_exception_suppression_gate.main([]) == 1
    report = json.loads((ev / "security_exception_suppression_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("broad_exception_suppression:bad.py:") for item in report["findings"])


def test_security_exception_suppression_gate_fails_on_broad_return(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "bad_return.py").write_text(
        "def f():\n    try:\n        return 1\n    except Exception:\n        return 0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_exception_suppression_gate, "ROOT", repo)
    monkeypatch.setattr(security_exception_suppression_gate, "evidence_root", lambda: repo / "evidence")
    assert security_exception_suppression_gate.main([]) == 1
    report = json.loads((ev / "security_exception_suppression_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("broad_exception_suppression:bad_return.py:") for item in report["findings"])
