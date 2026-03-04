from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECURITY_DIR = ROOT / "tooling" / "security"


def test_security_scripts_do_not_use_except_pass() -> None:
    violations: list[str] = []
    for path in sorted(SECURITY_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                body = node.body
                if len(body) == 1 and isinstance(body[0], ast.Pass):
                    rel = str(path.relative_to(ROOT)).replace("\\", "/")
                    line = getattr(body[0], "lineno", 0)
                    violations.append(f"{rel}:{line}")
    assert not violations, "except-pass is forbidden in tooling/security:\n" + "\n".join(violations)
