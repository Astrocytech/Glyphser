from __future__ import annotations

import json
from pathlib import Path

from tooling.security import signed_json_hash_equivalence_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_signed_json_hash_equivalence_snapshot_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    policy = repo / "governance" / "security" / "policy.json"
    _write_json(policy, {"a": 1})
    _write(policy.with_suffix(".json.sig"), "sig\n")

    monkeypatch.setattr(signed_json_hash_equivalence_gate, "ROOT", repo)
    monkeypatch.setattr(signed_json_hash_equivalence_gate, "SIGNED_JSON_ROOT", repo / "governance" / "security")
    monkeypatch.setattr(signed_json_hash_equivalence_gate, "evidence_root", lambda: ev)

    assert signed_json_hash_equivalence_gate.main([]) == 0
    report = json.loads((ev / "security" / "signed_json_hash_equivalence_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert "governance/security/policy.json" in report["hashes"]


def test_signed_json_hash_equivalence_compare_detects_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    left = repo / "left.json"
    right = repo / "right.json"

    _write_json(
        left,
        {
            "schema_version": 1,
            "hashes": {"governance/security/policy.json": {"json_sha256": "abc", "sig_sha256": "def"}},
        },
    )
    _write_json(
        right,
        {
            "schema_version": 1,
            "hashes": {"governance/security/policy.json": {"json_sha256": "xyz", "sig_sha256": "def"}},
        },
    )

    monkeypatch.setattr(signed_json_hash_equivalence_gate, "evidence_root", lambda: ev)
    assert signed_json_hash_equivalence_gate.main(["--left", str(left), "--right", str(right)]) == 1
    report = json.loads((ev / "security" / "signed_json_hash_equivalence_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "json_hash_mismatch:governance/security/policy.json" in report["findings"]
