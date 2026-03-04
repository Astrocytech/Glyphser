from __future__ import annotations

from tooling.security.review_policy_gate import _covers_required_path


def test_covers_required_path_matches_prefix_and_exact() -> None:
    declared = ["/tooling/security/", "/governance/security/*", "/.github/workflows/"]
    assert _covers_required_path("tooling/security/", declared)
    assert _covers_required_path("governance/security/", declared)
    assert _covers_required_path(".github/workflows/", declared)
    assert not _covers_required_path("runtime/glyphser/security/", declared)
