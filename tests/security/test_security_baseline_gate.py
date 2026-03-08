from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_baseline_gate_passes():
    subprocess.run([sys.executable, "tooling/security/security_artifacts.py"], cwd=ROOT, check=True)
    proc = subprocess.run(
        [sys.executable, "tooling/security/security_baseline_gate.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads((ROOT / "evidence" / "security" / "latest.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
