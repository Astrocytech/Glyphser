from __future__ import annotations

import json
from pathlib import Path

from tooling.security import provenance_revocation_gate


def test_provenance_revocation_gate_detects_revoked_digest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    target = sec / "a.json"
    target.write_text('{"x":1}\n', encoding="utf-8")
    import hashlib

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "provenance_revocation_list.json").write_text(
        json.dumps({"revoked_digests": [digest], "revoked_signatures": []}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(provenance_revocation_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_revocation_gate, "evidence_root", lambda: repo / "evidence")
    assert provenance_revocation_gate.main([]) == 1
