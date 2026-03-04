from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tooling" / "security" / "semgrep-rules.yml"
FIXTURES = ROOT / "tests" / "security" / "semgrep_fixtures"


@pytest.mark.skipif(shutil.which("semgrep") is None, reason="semgrep not installed")
def test_semgrep_rules_catch_expected_patterns() -> None:
    proc = subprocess.run(
        ["semgrep", "--config", str(CONFIG), "--json", str(FIXTURES / "bad.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert proc.returncode == 1, proc.stdout + "\n" + proc.stderr
    payload = json.loads(proc.stdout)
    ids = {r.get("check_id") for r in payload.get("results", [])}
    assert "glyphser.path-traversal-archive-extractall" in ids
    assert "glyphser.unsafe-tempfile-mktemp" in ids
    assert "glyphser.permissive-file-mode" in ids


@pytest.mark.skipif(shutil.which("semgrep") is None, reason="semgrep not installed")
def test_semgrep_rules_allow_good_fixture() -> None:
    proc = subprocess.run(
        ["semgrep", "--config", str(CONFIG), "--json", str(FIXTURES / "good.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
