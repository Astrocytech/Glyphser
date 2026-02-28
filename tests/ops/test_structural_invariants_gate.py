from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_structural_invariants_gate_passes() -> None:
    proc = subprocess.run(
        [sys.executable, "tooling/gates/structural_invariants_gate.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((ROOT / "evidence" / "structure" / "structural_invariants.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
