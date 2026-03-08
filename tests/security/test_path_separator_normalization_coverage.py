from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SECURITY_SCRIPTS = ROOT / "tooling" / "security"


def test_path_sensitive_security_scripts_normalize_path_separators() -> None:
    violations: list[str] = []
    for script in sorted(SECURITY_SCRIPTS.glob("*.py")):
        if script.name == "__init__.py":
            continue
        for line_no, line in enumerate(script.read_text(encoding="utf-8").splitlines(), start=1):
            if "relative_to(ROOT)" not in line:
                continue
            if ".parts" in line:
                continue
            if ".as_posix()" in line or '.replace("\\\\", "/")' in line:
                continue
            violations.append(f"{script.relative_to(ROOT)}:{line_no}")

    assert not violations, "path-sensitive callsites must normalize separators:\n" + "\n".join(violations)
