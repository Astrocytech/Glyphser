from __future__ import annotations

import json
from pathlib import Path

from tooling.security import governance_markdown_gate


def test_governance_markdown_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    meta = gov / "metadata"
    meta.mkdir(parents=True)
    (gov / "THREAT_MODEL.md").write_text("x\n", encoding="utf-8")
    mp = meta / "THREAT_MODEL.meta.json"
    mp.write_text(json.dumps({"title": "t", "owner": "o", "version": "1", "last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8")

    from runtime.glyphser.security.artifact_signing import current_key, sign_file

    (mp.with_suffix(".json.sig")).write_text(sign_file(mp, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (gov / "governance_markdown_manifest.json").write_text(
        json.dumps({"documents": [{"path": "governance/security/THREAT_MODEL.md", "metadata_path": "governance/security/metadata/THREAT_MODEL.meta.json", "signature_path": "governance/security/metadata/THREAT_MODEL.meta.json.sig"}]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(governance_markdown_gate, "ROOT", repo)
    monkeypatch.setattr(governance_markdown_gate, "evidence_root", lambda: repo / "evidence")
    assert governance_markdown_gate.main([]) == 0
