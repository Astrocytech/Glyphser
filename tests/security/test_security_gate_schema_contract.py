from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECURITY_DIR = ROOT / "tooling" / "security"


def test_every_gate_has_schema_contract_markers() -> None:
    violations: list[str] = []
    for path in sorted(SECURITY_DIR.glob("*_gate.py")):
        text = path.read_text(encoding="utf-8")
        if "write_json_report(" not in text:
            continue
        has_inline_contract = all(marker in text for marker in ['"status"', '"findings"', '"summary"', '"metadata"'])
        if not has_inline_contract:
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            violations.append(rel)
    assert not violations, "migrated gates missing schema contract markers:\n" + "\n".join(violations)
