from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tooling" / "security" / "semgrep-rules.yml"
FIXTURES = ROOT / "tests" / "security" / "semgrep_fixtures"


def _run_semgrep(path: Path) -> tuple[int, dict[str, object], str]:
    proc = subprocess.run(
        ["semgrep", "--config", str(CONFIG), "--json", str(path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    payload = json.loads(proc.stdout)
    return proc.returncode, payload, proc.stdout + "\n" + proc.stderr


def test_semgrep_rules_catch_expected_patterns() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "bad.py")
    assert rc in {0, 1}, output
    ids = {r.get("check_id") for r in payload.get("results", [])}
    assert any(str(i).endswith("glyphser.path-traversal-archive-extractall") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-tempfile-mktemp") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-tempfile-delete-false") for i in ids)
    assert any(str(i).endswith("glyphser.path-join-untrusted") for i in ids)
    assert any(str(i).endswith("glyphser.permissive-file-mode") for i in ids)


def test_semgrep_rules_allow_good_fixture() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "good.py")
    assert rc == 0, output
    assert payload.get("results", []) == []


def test_semgrep_rules_catch_extended_patterns() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "bad_extended.py")
    assert rc in {0, 1}, output
    ids = {r.get("check_id") for r in payload.get("results", [])}
    assert any(str(i).endswith("glyphser.subprocess-shell-true") for i in ids)
    assert any(str(i).endswith("glyphser.dynamic-code-execution") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-yaml-load") for i in ids)
    assert any(str(i).endswith("glyphser.unsafe-tempfile-delete-false") for i in ids)
    assert any(str(i).endswith("glyphser.permissive-file-mode") for i in ids)


def test_semgrep_rules_allow_extended_good_fixture() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "good_extended.py")
    assert rc == 0, output
    assert payload.get("results", []) == []
