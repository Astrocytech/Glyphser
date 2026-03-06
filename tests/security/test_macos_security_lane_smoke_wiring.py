from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_ci_includes_macos_security_tooling_smoke_lane() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "security-tooling-smoke-matrix:" in ci
    assert "os: [ubuntu-latest, macos-latest]" in ci
    assert "name: security-tooling-smoke-${{ matrix.os }}" in ci


def test_macos_smoke_lane_runs_key_security_gates() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "python tooling/security/security_toolchain_gate.py" in ci
    assert "python tooling/security/semgrep_rules_self_check_gate.py" in ci
    assert "python tooling/security/security_super_gate.py --strict-prereqs" in ci
    assert "python tooling/security/security_event_schema_gate.py" in ci
