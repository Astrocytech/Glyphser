from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_annual_independent_review_workflow_is_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-annual-independent-review.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "workflow_dispatch:" in wf
    assert "concurrency:" in wf
    assert "cancel-in-progress: false" in wf
    assert "python tooling/security/annual_independent_review_attestation.py --strict-key" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-annual-independent-review" in wf
    assert "annual_independent_review_attestation.json" in wf
    assert "annual_independent_review_attestation.json.sig" in wf
    assert "ANNUAL_INDEPENDENT_REVIEW_CHECKLIST.md" in wf

