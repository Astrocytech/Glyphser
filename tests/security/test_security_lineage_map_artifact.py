from __future__ import annotations

import hashlib
import json
import tracemalloc
from pathlib import Path

from tooling.security import security_lineage_map_artifact


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _canonical_sha256(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_security_lineage_map_artifact_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(sec / "policy_signature.json", {"status": "PASS", "summary": {}})
    _write(
        sec / "security_super_gate.json",
        {"results": [{"cmd": ["python", "tooling/security/policy_signature_gate.py"], "status": "PASS"}]},
    )
    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_lineage_map_artifact, "ROOT", repo)
    monkeypatch.setattr(security_lineage_map_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_lineage_map_artifact, "artifact_signing", _Signing)
    assert security_lineage_map_artifact.main([]) == 0
    report = json.loads((sec / "security_lineage_map.json").read_text(encoding="utf-8"))
    assert report["summary"]["lineage_mappings"] >= 3
    digest = json.loads((sec / "security_lineage_digest.json").read_text(encoding="utf-8"))
    assert digest["summary"]["lineage_digest_sha256"] == _canonical_sha256(report["mappings"])
    assert digest["summary"]["lineage_mappings"] == report["summary"]["lineage_mappings"]
    assert (sec / "security_lineage_digest.json.sig").read_text(encoding="utf-8").strip() == "sig"


def test_security_lineage_map_artifact_fails_on_invalid_json(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "broken.json").write_text("{", encoding="utf-8")
    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_lineage_map_artifact, "ROOT", repo)
    monkeypatch.setattr(security_lineage_map_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_lineage_map_artifact, "artifact_signing", _Signing)
    assert security_lineage_map_artifact.main([]) == 1
    report = json.loads((sec / "security_lineage_map.json").read_text(encoding="utf-8"))
    assert "invalid_report_json:security/broken.json" in report["findings"]
    digest = json.loads((sec / "security_lineage_digest.json").read_text(encoding="utf-8"))
    assert digest["status"] == "FAIL"


def test_security_lineage_map_artifact_scales_to_large_report_counts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(sec / "security_super_gate.json", {"results": []})
    for idx in range(1500):
        _write(sec / f"gate_{idx}.json", {"status": "PASS", "summary": {"i": idx}, "metadata": {"gate": f"gate_{idx}"}})

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_lineage_map_artifact, "ROOT", repo)
    monkeypatch.setattr(security_lineage_map_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_lineage_map_artifact, "artifact_signing", _Signing)
    assert security_lineage_map_artifact.main([]) == 0
    report = json.loads((sec / "security_lineage_map.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["reports_scanned"] == 1501


def test_security_lineage_map_artifact_stays_under_memory_ceiling(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(sec / "security_super_gate.json", {"results": []})
    payload = {"status": "PASS", "summary": {"values": list(range(300))}, "metadata": {"gate": "x"}}
    for idx in range(1000):
        _write(sec / f"gate_{idx}.json", payload)

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_lineage_map_artifact, "ROOT", repo)
    monkeypatch.setattr(security_lineage_map_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_lineage_map_artifact, "artifact_signing", _Signing)

    tracemalloc.start()
    try:
        assert security_lineage_map_artifact.main([]) == 0
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak <= 64 * 1024 * 1024


def test_security_lineage_map_artifact_uses_streaming_path_for_large_super_gate(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    # Inflate file size so the streaming parser path is exercised.
    large_results = [{"cmd": ["python", "tooling/security/policy_signature_gate.py"], "status": "PASS"} for _ in range(400)]
    _write(sec / "security_super_gate.json", {"results": large_results, "padding": "x" * 20000})
    _write(sec / "policy_signature_gate.json", {"status": "PASS"})

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_lineage_map_artifact, "ROOT", repo)
    monkeypatch.setattr(security_lineage_map_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_lineage_map_artifact, "artifact_signing", _Signing)
    monkeypatch.setattr(security_lineage_map_artifact, "LARGE_JSON_STREAM_THRESHOLD_BYTES", 256)
    assert security_lineage_map_artifact.main([]) == 0
    report = json.loads((sec / "security_lineage_map.json").read_text(encoding="utf-8"))
    assert any(
        item.get("rule_id") == "LINEAGE_SUPER_GATE_COMPONENT_STATUS"
        and "evidence/security/policy_signature_gate.json" in item.get("source_artifacts", [])
        for item in report.get("mappings", [])
        if isinstance(item, dict)
    )
