from __future__ import annotations

import json
from pathlib import Path

from tooling.security import cross_run_suspicious_pattern_linkage_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_cross_run_linkage_passes_without_repeat(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "WARN", "findings": ["tamper_signal_detected"]})

    monkeypatch.setattr(cross_run_suspicious_pattern_linkage_gate, "ROOT", repo)
    monkeypatch.setattr(cross_run_suspicious_pattern_linkage_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        cross_run_suspicious_pattern_linkage_gate,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "cross_run_suspicious_pattern_history.json",
    )

    assert cross_run_suspicious_pattern_linkage_gate.main([]) == 0
    report = json.loads((sec / "cross_run_suspicious_pattern_linkage_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["linked_repeated_patterns"] == 0


def test_cross_run_linkage_warns_on_repeated_pattern(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "gate_a.json", {"status": "WARN", "findings": ["tamper_signal_detected"]})
    _write(
        sec / "cross_run_suspicious_pattern_history.json",
        {
            "schema_version": 1,
            "counts": {
                "gate_a.json:tamper_signal_detected": 1,
            },
        },
    )

    monkeypatch.setattr(cross_run_suspicious_pattern_linkage_gate, "ROOT", repo)
    monkeypatch.setattr(cross_run_suspicious_pattern_linkage_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        cross_run_suspicious_pattern_linkage_gate,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "cross_run_suspicious_pattern_history.json",
    )

    assert cross_run_suspicious_pattern_linkage_gate.main([]) == 0
    report = json.loads((sec / "cross_run_suspicious_pattern_linkage_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["linked_repeated_patterns"] == 1
    assert any(str(item).startswith("repeated_suspicious_pattern:gate_a.json:tamper_signal_detected:count:2") for item in report["findings"])
