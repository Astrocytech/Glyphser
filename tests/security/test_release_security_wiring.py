from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_workflow_enforces_signature_verification() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "verify-signatures:" in release
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in release
    assert "python tooling/security/slsa_attestation_gate.py" in release
    assert "python tooling/security/secret_management_gate.py" in release
    assert "python tooling/security/production_controls_gate.py" in release
    assert "GLYPHSER_STRICT_SIGNING: \"true\"" in release
    assert "GLYPHSER_PROVENANCE_HMAC_KEY: ${{ secrets.GLYPHSER_PROVENANCE_HMAC_KEY }}" in release


def test_release_workflow_avoids_unpinned_action_tags() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "actions/download-artifact@" not in release
    assert "gh-action-pypi-publish@" not in release
