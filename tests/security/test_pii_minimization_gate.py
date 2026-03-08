from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import pii_minimization_gate


def _write(path: Path, payload: object | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_pii_minimization_gate_passes_without_pii(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "pii_minimization_policy.json"
    _write(
        policy,
        {
            "scan_globs": ["evidence/security/*.json"],
            "forbidden_patterns": {"email": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"},
            "allowed_tokens": ["REDACTED"],
        },
    )
    _sign(policy)
    _write(repo / "evidence" / "security" / "safe.json", {"operator": "REDACTED"})

    monkeypatch.setattr(pii_minimization_gate, "ROOT", repo)
    monkeypatch.setattr(pii_minimization_gate, "POLICY", policy)
    monkeypatch.setattr(pii_minimization_gate, "evidence_root", lambda: repo / "evidence")
    assert pii_minimization_gate.main([]) == 0


def test_pii_minimization_gate_fails_when_pii_detected(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "pii_minimization_policy.json"
    _write(
        policy,
        {
            "scan_globs": ["evidence/security/*.json"],
            "forbidden_patterns": {"email": "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"},
            "allowed_tokens": ["REDACTED"],
        },
    )
    _sign(policy)
    _write(repo / "evidence" / "security" / "unsafe.json", {"owner_email": "operator@glyphser.local"})

    monkeypatch.setattr(pii_minimization_gate, "ROOT", repo)
    monkeypatch.setattr(pii_minimization_gate, "POLICY", policy)
    monkeypatch.setattr(pii_minimization_gate, "evidence_root", lambda: repo / "evidence")
    assert pii_minimization_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "pii_minimization_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("pii_pattern_detected:email:") for item in report["findings"])
