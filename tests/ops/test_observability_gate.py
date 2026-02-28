from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_observability_gate_passes():
    proc = subprocess.run(
        [sys.executable, "tooling/gates/observability_gate.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    latest = json.loads((ROOT / "evidence" / "observability" / "latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "PASS"
    assert latest["slo_overall"] == "PASS"
