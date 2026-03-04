from __future__ import annotations

import json
import tarfile
from pathlib import Path

from tooling.security import tabletop_replay


def test_tabletop_replay_passes_for_bundle_with_required_pass_reports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    build = tmp_path / "build"
    sec = build / "security"
    sec.mkdir(parents=True, exist_ok=True)
    for name in (
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "provenance_revocation_gate.json",
    ):
        (sec / name).write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    bundle = repo / "bundle.tar.gz"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "w:gz") as tf:
        for path in sorted(sec.glob("*.json")):
            tf.add(path, arcname=f"security/{path.name}")
    monkeypatch.setattr(tabletop_replay, "ROOT", repo)
    monkeypatch.setattr(tabletop_replay, "evidence_root", lambda: repo / "evidence")
    assert tabletop_replay.main(["--bundle", str(bundle)]) == 0
