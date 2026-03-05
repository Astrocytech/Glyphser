from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_auto_reopen_on_regression


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_auto_reopen_on_regression_reopens_done_item(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "negative_test_evidence_ref": "",
                    "verification": {
                        "regression_detected": True,
                        "regression_repro_ref": "gate:runtime_api_state_schema_gate:regression-42",
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(hardening_auto_reopen_on_regression, "ROOT", repo)
    monkeypatch.setattr(hardening_auto_reopen_on_regression, "REGISTRY", registry)
    monkeypatch.setattr(hardening_auto_reopen_on_regression, "evidence_root", lambda: repo / "evidence")

    assert hardening_auto_reopen_on_regression.main([]) == 0
    updated = json.loads(registry.read_text(encoding="utf-8"))
    row = updated["entries"][0]
    assert row["status"] == "in_progress"
    assert row["previous_status"] == "done"
    assert row["reopen_reason"] == "regression_detected"
    assert row["negative_test_evidence_ref"] == "gate:runtime_api_state_schema_gate:regression-42"


def test_hardening_auto_reopen_on_regression_leaves_non_regressed_done_item(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {
                    "id": "SEC-HARD-0001",
                    "status": "done",
                    "previous_status": "in_progress",
                    "negative_test_evidence_ref": "gate:some-fail",
                    "verification": {
                        "regression_detected": False,
                        "regression_repro_ref": "",
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(hardening_auto_reopen_on_regression, "ROOT", repo)
    monkeypatch.setattr(hardening_auto_reopen_on_regression, "REGISTRY", registry)
    monkeypatch.setattr(hardening_auto_reopen_on_regression, "evidence_root", lambda: repo / "evidence")

    assert hardening_auto_reopen_on_regression.main([]) == 0
    updated = json.loads(registry.read_text(encoding="utf-8"))
    row = updated["entries"][0]
    assert row["status"] == "done"
    assert row["previous_status"] == "in_progress"
