from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_preflight


def test_security_preflight_passes_with_required_inputs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "tooling" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "policy_signature_manifest.json").write_text("{}\n", encoding="utf-8")
    (repo / "tooling" / "security" / "security_toolchain_lock.json").write_text("{}\n", encoding="utf-8")
    (repo / "tooling" / "security" / "security_super_gate_manifest.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(security_preflight, "ROOT", repo)
    monkeypatch.setattr(security_preflight.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "k")
    assert security_preflight.main(["--strict"]) == 0


def test_security_preflight_fails_with_diagnostics(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(security_preflight, "ROOT", repo)
    monkeypatch.setattr(security_preflight.shutil, "which", lambda _name: None)
    monkeypatch.delenv("TZ", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)
    assert security_preflight.main(["--strict"]) == 1
    payload = json.loads((repo / "evidence" / "security" / "security_preflight.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert payload["diagnostics"]
