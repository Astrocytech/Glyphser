from __future__ import annotations

import json
from pathlib import Path

from tooling.security import crypto_parameter_review_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_crypto_parameter_review_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    _write(
        gov / "crypto_parameter_policy.json",
        {
            "min_hmac_key_bytes": 32,
            "allowed_hash_algorithms": ["sha256"],
            "forbidden_hash_algorithms": ["md5", "sha1"],
            "review_max_age_days": 365,
            "last_reviewed_utc": "2026-01-01T00:00:00+00:00",
        },
    )
    monkeypatch.setattr(crypto_parameter_review_gate, "ROOT", repo)
    monkeypatch.setattr(crypto_parameter_review_gate, "POLICY", gov / "crypto_parameter_policy.json")
    monkeypatch.setattr(crypto_parameter_review_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "x" * 64)
    assert crypto_parameter_review_gate.main([]) == 0


def test_crypto_parameter_review_gate_fails_for_weak_or_stale_settings(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(
        gov / "crypto_parameter_policy.json",
        {
            "min_hmac_key_bytes": 8,
            "allowed_hash_algorithms": ["sha256", "md5"],
            "forbidden_hash_algorithms": ["sha1"],
            "review_max_age_days": 1,
            "last_reviewed_utc": "2020-01-01T00:00:00+00:00",
        },
    )
    monkeypatch.setattr(crypto_parameter_review_gate, "ROOT", repo)
    monkeypatch.setattr(crypto_parameter_review_gate, "POLICY", gov / "crypto_parameter_policy.json")
    monkeypatch.setattr(crypto_parameter_review_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "short-key")
    assert crypto_parameter_review_gate.main([]) == 1
    report = json.loads((sec / "crypto_parameter_review_gate.json").read_text(encoding="utf-8"))
    assert "min_hmac_key_bytes_below_threshold" in report["findings"]
    assert any(item.startswith("crypto_parameter_review_stale:") for item in report["findings"])
