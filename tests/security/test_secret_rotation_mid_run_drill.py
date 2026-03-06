from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import secret_rotation_mid_run_drill


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_secret_rotation_mid_run_drill_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "secret_rotation_mid_run_drill.json"
    _write(
        drill,
        {
            "status": "PASS",
            "run_id": "DRILL-1",
            "rotated_secret_refs": ["GLYPHSER_PROVENANCE_HMAC_KEY"],
            "expected_gate_behavior": "Fail closed then recover with rotated secret.",
            "resumed_with_new_secret": True,
            "fallback_used_old_secret": False,
        },
    )
    _sign(drill)

    monkeypatch.setattr(secret_rotation_mid_run_drill, "ROOT", repo)
    monkeypatch.setattr(secret_rotation_mid_run_drill, "DRILL", drill)
    monkeypatch.setattr(secret_rotation_mid_run_drill, "evidence_root", lambda: repo / "evidence")
    assert secret_rotation_mid_run_drill.main([]) == 0


def test_secret_rotation_mid_run_drill_fails_on_missing_requirements(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "secret_rotation_mid_run_drill.json"
    _write(
        drill,
        {
            "status": "FAIL",
            "run_id": "",
            "rotated_secret_refs": [],
            "expected_gate_behavior": "",
            "resumed_with_new_secret": False,
            "fallback_used_old_secret": True,
        },
    )
    _sign(drill)

    monkeypatch.setattr(secret_rotation_mid_run_drill, "ROOT", repo)
    monkeypatch.setattr(secret_rotation_mid_run_drill, "DRILL", drill)
    monkeypatch.setattr(secret_rotation_mid_run_drill, "evidence_root", lambda: repo / "evidence")
    assert secret_rotation_mid_run_drill.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "secret_rotation_mid_run_drill.json").read_text(encoding="utf-8"))
    assert "missing_run_id" in report["findings"]
    assert "missing_rotated_secret_refs" in report["findings"]
    assert "run_not_resumed_with_new_secret" in report["findings"]
    assert "fallback_used_old_secret" in report["findings"]
