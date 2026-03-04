from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_promotion_dry_run_workflow_exists_and_runs_promotion_gate() -> None:
    wf = (ROOT / ".github" / "workflows" / "promotion-dry-run.yml").read_text(encoding="utf-8")
    assert "name: Promotion Dry Run" in wf
    assert "python tooling/security/promotion_policy_gate.py" in wf
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in wf
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/promotion-dry-run" in wf
