from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_control_recertification


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_control_recertification_writes_signed_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(repo / "tooling" / "security" / "security_super_gate_manifest.json", {"core": ["a.py"], "extended": ["b.py"]})

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = path, key
            return "sig"

    monkeypatch.setattr(security_control_recertification, "ROOT", repo)
    monkeypatch.setattr(security_control_recertification, "MANIFEST", repo / "tooling" / "security" / "security_super_gate_manifest.json")
    monkeypatch.setattr(security_control_recertification, "artifact_signing", _Signing)
    monkeypatch.setattr(security_control_recertification, "evidence_root", lambda: ev)

    assert security_control_recertification.main([]) == 0
    report = json.loads((ev / "security" / "security_control_recertification.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert (ev / "security" / "security_control_recertification.json.sig").read_text(encoding="utf-8").strip() == "sig"
