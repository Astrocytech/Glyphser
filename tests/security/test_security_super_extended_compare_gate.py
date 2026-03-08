from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import security_super_extended_compare_gate


def test_super_extended_compare_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps(
            {
                "results": [
                    {"cmd": ["python", "tooling/security/a.py"], "status": "FAIL"},
                    {"cmd": ["python", "tooling/security/b.py"], "status": "PASS"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 0


def test_super_extended_compare_gate_fails_on_unknown_failure(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps({"results": [{"cmd": ["python", "tooling/security/unknown.py"], "status": "FAIL"}]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 1


def test_super_extended_compare_gate_fails_when_extended_failure_ages_without_exception(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps({"results": [{"cmd": ["python", "tooling/security/b.py"], "status": "FAIL"}]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    (ev / "security_super_extended_failure_history.json").write_text(
        json.dumps(
            {
                "entries": {
                    "tooling/security/b.py": {
                        "first_seen_utc": "2026-01-01T00:00:00+00:00",
                        "last_seen_utc": "2026-01-01T00:00:00+00:00",
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "HISTORY", ev / "security_super_extended_failure_history.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "EXCEPTION_REGISTRY",
        repo / "governance" / "security" / "temporary_exceptions.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "EXTENDED_FAILURE_MAX_AGE_DAYS", 1)
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 1
    report = json.loads((ev / "security_super_extended_compare_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("extended_failure_core_blocker:tooling/security/b.py") for item in report["findings"])


def test_super_extended_compare_gate_allows_aged_failure_with_signed_exception(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps({"results": [{"cmd": ["python", "tooling/security/b.py"], "status": "FAIL"}]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    (ev / "security_super_extended_failure_history.json").write_text(
        json.dumps(
            {
                "entries": {
                    "tooling/security/b.py": {
                        "first_seen_utc": "2026-01-01T00:00:00+00:00",
                        "last_seen_utc": "2026-01-01T00:00:00+00:00",
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    registry = gov / "temporary_exceptions.json"
    registry.write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "id": "EXC-1",
                        "scope": "extended_failure:tooling/security/b.py",
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    registry.with_suffix(".json.sig").write_text(sign_file(registry, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "HISTORY", ev / "security_super_extended_failure_history.json")
    monkeypatch.setattr(security_super_extended_compare_gate, "EXCEPTION_REGISTRY", registry)
    monkeypatch.setattr(security_super_extended_compare_gate, "EXTENDED_FAILURE_MAX_AGE_DAYS", 1)
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 0
