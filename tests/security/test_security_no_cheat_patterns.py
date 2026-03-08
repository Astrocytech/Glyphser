from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECURITY_DIR = ROOT / "tooling" / "security"

PASS_SUPPRESSION_RE = re.compile(r"except\s+Exception\s*:\s*\n\s*pass\b", re.MULTILINE)
FORCED_SUCCESS_RE = re.compile(r"except\s+Exception[\s\S]{0,240}?SystemExit\(0\)", re.MULTILINE)


def test_security_scripts_do_not_suppress_exceptions_with_pass() -> None:
    violations: list[str] = []
    for path in sorted(SECURITY_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if PASS_SUPPRESSION_RE.search(text):
            violations.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    assert not violations, "Exception suppression via `pass` is not allowed:\n" + "\n".join(violations)


def test_security_scripts_do_not_force_success_after_broad_exception() -> None:
    violations: list[str] = []
    for path in sorted(SECURITY_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if FORCED_SUCCESS_RE.search(text):
            violations.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    assert not violations, "Broad exception blocks must not force success exits:\n" + "\n".join(violations)
