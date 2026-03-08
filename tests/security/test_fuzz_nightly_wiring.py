from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_fuzz_nightly_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "fuzz-nightly.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "pytest -q tests/fuzz" in wf
    assert "fuzz-nightly-results" in wf
