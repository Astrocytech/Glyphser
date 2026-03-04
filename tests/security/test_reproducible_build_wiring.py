from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_reproducible_build_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "reproducible-build.yml").read_text(encoding="utf-8")
    assert "matrix:" in wf
    assert "os: [ubuntu-latest, macos-latest]" in wf
    assert "python tooling/security/reproducible_build_gate.py" in wf
