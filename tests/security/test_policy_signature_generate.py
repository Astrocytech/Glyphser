from __future__ import annotations

import json
from pathlib import Path

from tooling.security import policy_signature_generate


def test_policy_signature_generate_writes_signatures(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "x.json"
    policy.write_text('{"x":1}\n', encoding="utf-8")
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"files": ["governance/security/x.json"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(policy_signature_generate, "ROOT", repo)
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "unit-test-key")
    assert policy_signature_generate.main([]) == 0
    assert (gov / "x.json.sig").exists()
