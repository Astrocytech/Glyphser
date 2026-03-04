from __future__ import annotations

from pathlib import Path

import pytest

from tooling.security import evidence_run_dir_guard


def test_evidence_run_dir_guard_write_once(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(evidence_run_dir_guard, "evidence_root", lambda: tmp_path / "evidence" / "runs" / "abc")
    assert evidence_run_dir_guard.main(["--run-id", "abc"]) == 0
    with pytest.raises(ValueError, match="already initialized"):
        evidence_run_dir_guard.main(["--run-id", "abc"])
