from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RISKY_PARSING_OR_VERIFICATION_SCRIPTS = [
    ROOT / "tooling" / "security" / "external_audit_simulation.py",
    ROOT / "tooling" / "security" / "independent_verifier_profile_gate.py",
]


def test_risky_parsing_and_verification_scripts_use_subprocess_policy() -> None:
    for path in RISKY_PARSING_OR_VERIFICATION_SCRIPTS:
        text = path.read_text(encoding="utf-8")
        assert "run_checked(" in text, f"{path.name} must use subprocess_policy.run_checked"
        assert "subprocess.run(" not in text, f"{path.name} must not call subprocess.run directly"
