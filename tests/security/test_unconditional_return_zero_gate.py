from __future__ import annotations

import json
from pathlib import Path

from tooling.security import unconditional_return_zero_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_unconditional_return_zero_gate_fails_on_unconditional_success(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec_dir = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    _write(sec_dir / "bad_gate.py", "def main(argv=None):\n    return 0\n")
    monkeypatch.setattr(unconditional_return_zero_gate, "ROOT", repo)
    monkeypatch.setattr(unconditional_return_zero_gate, "evidence_root", lambda: repo / "evidence")
    assert unconditional_return_zero_gate.main([]) == 1
    report = json.loads((ev / "unconditional_return_zero_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("unconditional_return_zero:bad_gate.py:") for item in report["findings"])


def test_unconditional_return_zero_gate_passes_when_main_has_nonzero_failure_path(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec_dir = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    _write(
        sec_dir / "good_gate.py",
        "def main(argv=None):\n    status = 'PASS'\n    if status == 'PASS':\n        return 0\n    return 1\n",
    )
    monkeypatch.setattr(unconditional_return_zero_gate, "ROOT", repo)
    monkeypatch.setattr(unconditional_return_zero_gate, "evidence_root", lambda: repo / "evidence")
    assert unconditional_return_zero_gate.main([]) == 0
    report = json.loads((ev / "unconditional_return_zero_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
