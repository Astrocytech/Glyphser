from __future__ import annotations

import json
from pathlib import Path

from tooling.security import incident_bundle_collect


def test_incident_bundle_collect_writes_bundle_and_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    for name in ("policy_signature.json", "provenance_signature.json", "security_super_gate.json"):
        (sec / name).write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(incident_bundle_collect, "ROOT", repo)
    monkeypatch.setattr(incident_bundle_collect, "evidence_root", lambda: repo / "evidence")
    assert incident_bundle_collect.main(["--incident-id", "INC-1"]) == 0
    assert (repo / "evidence" / "incident" / "incident-bundle-INC-1.tar.gz").exists()
    digest_file = repo / "evidence" / "incident" / "incident-bundle-INC-1.tar.gz.sha256"
    assert digest_file.exists()
    manifest = repo / "evidence" / "incident" / "incident-bundle-INC-1.manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["incident_id"] == "INC-1"
    assert payload["bundle_sha256"]
    assert payload["bundle_sha256_path"].endswith("incident-bundle-INC-1.tar.gz.sha256")
