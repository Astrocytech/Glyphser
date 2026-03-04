from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tooling" / "security" / "semgrep-rules.yml"
FIXTURES = ROOT / "tests" / "security" / "semgrep_fixtures"


def test_semgrep_rules_catch_expected_patterns() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    proc = subprocess.run(
        ["semgrep", "--config", str(CONFIG), "--json", str(FIXTURES / "bad.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert proc.returncode in {0, 1}, proc.stdout + "\n" + proc.stderr
    payload = json.loads(proc.stdout)
    ids = {r.get("check_id") for r in payload.get("results", [])}
    assert any(str(i).endswith("glyphser.path-traversal-archive-extractall") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-tempfile-mktemp") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-tempfile-delete-false") for i in ids)
    assert any(str(i).endswith("glyphser.path-join-untrusted") for i in ids)
    assert any(str(i).endswith("glyphser.permissive-file-mode") for i in ids)


def test_semgrep_rules_allow_good_fixture() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    proc = subprocess.run(
        ["semgrep", "--config", str(CONFIG), "--json", str(FIXTURES / "good.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
