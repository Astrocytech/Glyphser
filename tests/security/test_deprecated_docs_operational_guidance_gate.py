from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deprecated_docs_operational_guidance_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_deprecated_docs_operational_guidance_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "deprecated_docs_policy.json",
        {
            "deprecated_docs": ["docs/deprecated/OLD.md"],
            "required_markers": ["DEPRECATED", "DO NOT USE"],
            "operational_guidance_docs": ["docs/START-HERE.md"],
        },
    )
    _write(repo / "docs" / "deprecated" / "OLD.md", "DEPRECATED\nDO NOT USE\n")
    _write(repo / "docs" / "START-HERE.md", "Use current docs only.\n")

    monkeypatch.setattr(deprecated_docs_operational_guidance_gate, "ROOT", repo)
    monkeypatch.setattr(
        deprecated_docs_operational_guidance_gate,
        "POLICY",
        repo / "governance" / "security" / "deprecated_docs_policy.json",
    )
    monkeypatch.setattr(deprecated_docs_operational_guidance_gate, "evidence_root", lambda: repo / "evidence")
    assert deprecated_docs_operational_guidance_gate.main([]) == 0


def test_deprecated_docs_operational_guidance_gate_fails_on_missing_marker_and_reference(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "deprecated_docs_policy.json",
        {
            "deprecated_docs": ["docs/deprecated/OLD.md"],
            "required_markers": ["DEPRECATED", "DO NOT USE"],
            "operational_guidance_docs": ["docs/START-HERE.md"],
        },
    )
    _write(repo / "docs" / "deprecated" / "OLD.md", "DEPRECATED only\n")
    _write(repo / "docs" / "START-HERE.md", "See docs/deprecated/OLD.md\n")

    monkeypatch.setattr(deprecated_docs_operational_guidance_gate, "ROOT", repo)
    monkeypatch.setattr(
        deprecated_docs_operational_guidance_gate,
        "POLICY",
        repo / "governance" / "security" / "deprecated_docs_policy.json",
    )
    monkeypatch.setattr(deprecated_docs_operational_guidance_gate, "evidence_root", lambda: repo / "evidence")
    assert deprecated_docs_operational_guidance_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "deprecated_docs_operational_guidance_gate.json").read_text(encoding="utf-8")
    )
    assert any(item.startswith("deprecated_doc_missing_marker:") for item in report["findings"])
    assert any(item.startswith("deprecated_doc_referenced_in_operational_guidance:") for item in report["findings"])
