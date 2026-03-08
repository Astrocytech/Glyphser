from __future__ import annotations

import json
import os
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import executable_review_annotation_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def _make_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
    os.chmod(path, 0o755)


def test_executable_review_annotation_gate_passes_for_approved_executables(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    baseline = repo / "governance" / "security" / "executable_review_annotations.json"
    executable = repo / "tooling" / "security" / "approved.sh"
    _make_executable(executable)
    _write(
        baseline,
        {
            "security_critical_paths": ["tooling/security"],
            "approved_executables": {
                "tooling/security/approved.sh": {"review_annotation": "SEC-REVIEW-1"}
            },
        },
    )
    _sign(baseline)

    monkeypatch.setattr(executable_review_annotation_gate, "ROOT", repo)
    monkeypatch.setattr(executable_review_annotation_gate, "BASELINE", baseline)
    monkeypatch.setattr(executable_review_annotation_gate, "evidence_root", lambda: repo / "evidence")
    assert executable_review_annotation_gate.main([]) == 0


def test_executable_review_annotation_gate_fails_for_new_unannotated_executable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    baseline = repo / "governance" / "security" / "executable_review_annotations.json"
    executable = repo / "tooling" / "security" / "new.sh"
    _make_executable(executable)
    _write(
        baseline,
        {
            "security_critical_paths": ["tooling/security"],
            "approved_executables": {},
        },
    )
    _sign(baseline)

    monkeypatch.setattr(executable_review_annotation_gate, "ROOT", repo)
    monkeypatch.setattr(executable_review_annotation_gate, "BASELINE", baseline)
    monkeypatch.setattr(executable_review_annotation_gate, "evidence_root", lambda: repo / "evidence")
    assert executable_review_annotation_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "executable_review_annotation_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("new_executable_without_review_annotation:tooling/security/new.sh") for item in report["findings"])
