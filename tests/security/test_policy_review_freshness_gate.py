from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import policy_review_freshness_gate


def test_policy_review_freshness_gate_passes_for_fresh_metadata(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    meta = gov / "metadata"
    ev = repo / "evidence" / "security"
    meta.mkdir(parents=True)
    ev.mkdir(parents=True)
    (gov / "OPERATIONS.md").write_text("# ops\n", encoding="utf-8")
    record = meta / "OPERATIONS.meta.json"
    record.write_text(json.dumps({"last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8")
    record.with_suffix(".json.sig").write_text(sign_file(record, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(policy_review_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(policy_review_freshness_gate, "GOV_SECURITY_DIR", gov)
    monkeypatch.setattr(policy_review_freshness_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(policy_review_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_POLICY_REVIEW_MAX_AGE_DAYS", "365")
    assert policy_review_freshness_gate.main([]) == 0


def test_policy_review_freshness_gate_fails_when_missing_metadata_in_strict_mode(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    meta = gov / "metadata"
    ev = repo / "evidence" / "security"
    meta.mkdir(parents=True)
    ev.mkdir(parents=True)
    (gov / "OPERATIONS.md").write_text("# ops\n", encoding="utf-8")

    monkeypatch.setattr(policy_review_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(policy_review_freshness_gate, "GOV_SECURITY_DIR", gov)
    monkeypatch.setattr(policy_review_freshness_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(policy_review_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_POLICY_REVIEW_REQUIRE_METADATA", "true")
    assert policy_review_freshness_gate.main([]) == 1
    report = json.loads((ev / "policy_review_freshness_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_metadata:OPERATIONS.md" in report["findings"]


def test_policy_review_freshness_gate_fails_when_metadata_signature_invalid(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    meta = gov / "metadata"
    ev = repo / "evidence" / "security"
    meta.mkdir(parents=True)
    ev.mkdir(parents=True)
    (gov / "OPERATIONS.md").write_text("# ops\n", encoding="utf-8")
    record = meta / "OPERATIONS.meta.json"
    record.write_text(json.dumps({"last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8")
    record.with_suffix(".json.sig").write_text("bad\n", encoding="utf-8")

    monkeypatch.setattr(policy_review_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(policy_review_freshness_gate, "GOV_SECURITY_DIR", gov)
    monkeypatch.setattr(policy_review_freshness_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(policy_review_freshness_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_review_freshness_gate.main([]) == 1
    report = json.loads((ev / "policy_review_freshness_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("invalid_metadata_signature:") for item in report["findings"])


def test_parse_iso_accepts_dst_boundary_offsets() -> None:
    pre = policy_review_freshness_gate._parse_iso("2026-03-08T01:59:59-05:00")
    post = policy_review_freshness_gate._parse_iso("2026-03-08T03:00:00-04:00")
    assert isinstance(pre, datetime)
    assert isinstance(post, datetime)
    assert pre.utcoffset() is not None
    assert post.utcoffset() is not None


def test_parse_iso_rejects_leap_second_timestamp() -> None:
    assert policy_review_freshness_gate._parse_iso("2016-12-31T23:59:60Z") is None


def test_policy_review_freshness_gate_fails_on_clock_consistency_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    meta = gov / "metadata"
    ev = repo / "evidence" / "security"
    meta.mkdir(parents=True)
    ev.mkdir(parents=True)
    (gov / "OPERATIONS.md").write_text("# ops\n", encoding="utf-8")
    record = meta / "OPERATIONS.meta.json"
    record.write_text(json.dumps({"last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8")
    record.with_suffix(".json.sig").write_text(sign_file(record, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(policy_review_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(policy_review_freshness_gate, "GOV_SECURITY_DIR", gov)
    monkeypatch.setattr(policy_review_freshness_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(policy_review_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        policy_review_freshness_gate,
        "clock_consistency_violation",
        lambda _now: "clock_consistency_violation:wall_vs_monotonic_drift_seconds:11.000:tolerance_seconds:5.000",
    )
    assert policy_review_freshness_gate.main([]) == 1
    report = json.loads((ev / "policy_review_freshness_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("clock_consistency_violation:") for item in report["findings"])
