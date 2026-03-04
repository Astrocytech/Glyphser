from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import security_toolchain_lock_signature_gate


def test_security_toolchain_lock_signature_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "security_toolchain_lock.json").write_text('{"semgrep":{"version":"1.95.0"}}\n', encoding="utf-8")
    (sec / "security_toolchain_transitive_lock.json").write_text('{"semgrep":{"transitive":[]}}\n', encoding="utf-8")
    for path in [
        sec / "security_toolchain_lock.json",
        sec / "security_toolchain_transitive_lock.json",
    ]:
        path.with_suffix(path.suffix + ".sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n")

    monkeypatch.setattr(security_toolchain_lock_signature_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_toolchain_lock_signature_gate,
        "LOCK_FILES",
        [
            sec / "security_toolchain_lock.json",
            sec / "security_toolchain_transitive_lock.json",
        ],
    )
    monkeypatch.setattr(security_toolchain_lock_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert security_toolchain_lock_signature_gate.main([]) == 0


def test_security_toolchain_lock_signature_gate_fails_when_missing_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "security_toolchain_lock.json").write_text('{"semgrep":{"version":"1.95.0"}}\n', encoding="utf-8")
    (sec / "security_toolchain_transitive_lock.json").write_text('{"semgrep":{"transitive":[]}}\n', encoding="utf-8")
    (sec / "security_toolchain_lock.json.sig").write_text(
        sign_file(sec / "security_toolchain_lock.json", key=current_key(strict=False)) + "\n"
    )

    monkeypatch.setattr(security_toolchain_lock_signature_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_toolchain_lock_signature_gate,
        "LOCK_FILES",
        [
            sec / "security_toolchain_lock.json",
            sec / "security_toolchain_transitive_lock.json",
        ],
    )
    monkeypatch.setattr(security_toolchain_lock_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert security_toolchain_lock_signature_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "security_toolchain_lock_signature_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "FAIL"
    assert any("missing_signature" in finding for finding in report["findings"])
