from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_push_button_workflow_enforces_policy_signature_gate() -> None:
    wf = (ROOT / ".github" / "workflows" / "push-button.yml").read_text(encoding="utf-8")
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/push-button" in wf
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in wf
    assert "python tooling/security/policy_signature_gate.py --strict-key" in wf
