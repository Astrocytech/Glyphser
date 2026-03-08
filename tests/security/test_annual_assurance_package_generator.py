from __future__ import annotations

import json
from pathlib import Path

from tooling.security import annual_assurance_package_generator


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_annual_assurance_package_generator_passes_with_required_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    for rel in annual_assurance_package_generator.REQUIRED_EVIDENCE:
        _write(ev / rel, {"status": "PASS"})
    monkeypatch.setattr(annual_assurance_package_generator, "ROOT", repo)
    monkeypatch.setattr(annual_assurance_package_generator, "evidence_root", lambda: ev)
    assert annual_assurance_package_generator.main([]) == 0
    report = json.loads((ev / "security" / "annual_assurance_package.json").read_text(encoding="utf-8"))
    assert report["summary"]["auditor_package_ready"] is True


def test_annual_assurance_package_generator_fails_when_evidence_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(ev / "security" / "security_super_gate.json", {"status": "PASS"})
    monkeypatch.setattr(annual_assurance_package_generator, "ROOT", repo)
    monkeypatch.setattr(annual_assurance_package_generator, "evidence_root", lambda: ev)
    assert annual_assurance_package_generator.main([]) == 1
    report = json.loads((ev / "security" / "annual_assurance_package.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_assurance_evidence:") for item in report["findings"])
