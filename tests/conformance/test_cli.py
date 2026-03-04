from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_conformance_cli_run_passes_as_script_path():
    proc = subprocess.run(
        [sys.executable, "tooling/conformance/cli.py", "run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
