from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tooling" / "security" / "semgrep-rules.yml"
FIXTURES = ROOT / "tests" / "security" / "semgrep_fixtures"
EXPECTED = json.loads((FIXTURES / "expected_findings.json").read_text(encoding="utf-8"))


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


def _assert_expected_findings(payload: dict[str, object], fixture_name: str) -> None:
    ids = {str(r.get("check_id", "")) for r in payload.get("results", []) if isinstance(r, dict)}
    expected = EXPECTED.get(fixture_name, [])
    assert isinstance(expected, list)
    for row in expected:
        assert isinstance(row, dict)
        suffix = str(row.get("check_id_suffix", ""))
        reason = str(row.get("reason", ""))
        assert suffix, f"missing check_id_suffix for {fixture_name}"
        assert reason, f"missing reason label for {fixture_name}:{suffix}"
        assert any(i.endswith(suffix) for i in ids), f"missing finding {suffix} ({reason})"


def test_semgrep_rules_catch_expected_patterns() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "bad.py")
    assert rc in {0, 1}, output
    _assert_expected_findings(payload, "bad.py")


def test_semgrep_rules_allow_good_fixture() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "good.py")
    assert rc == 0, output
    assert payload.get("results", []) == []


def test_semgrep_rules_catch_extended_patterns() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "bad_extended.py")
    assert rc in {0, 1}, output
    _assert_expected_findings(payload, "bad_extended.py")


def test_semgrep_rules_allow_extended_good_fixture() -> None:
    assert shutil.which("semgrep") is not None, "semgrep must be installed for security tests"
    rc, payload, output = _run_semgrep(FIXTURES / "good_extended.py")
    assert rc == 0, output
    assert payload.get("results", []) == []
