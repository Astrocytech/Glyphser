from __future__ import annotations

import json
from pathlib import Path

from tooling.security import replay_abuse_regression_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_replay_abuse_regression_gate_includes_distributed_low_rate_corpus_case(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    corpus = repo / "artifacts" / "inputs" / "security" / "replay_abuse_regression_corpus.json"
    _write(
        corpus,
        {
            "schema_version": 1,
            "cases": [
                {
                    "name": "distributed_low_rate_evasion",
                    "expected_classifier": {
                        "verdict": "normal",
                        "reason_code": "low_signal",
                        "score": 12,
                    },
                    "events": [
                        {"actor_id": "actor-01", "kind": "replay"},
                        {"actor_id": "actor-02", "kind": "replay"},
                        {"actor_id": "actor-03", "kind": "replay"},
                    ],
                },
                {
                    "name": "mixed_valid_invalid_token_spray",
                    "expected_classifier": {
                        "verdict": "normal",
                        "reason_code": "low_signal",
                        "score": 12,
                    },
                    "events": [
                        {"actor_id": "token-valid-01", "kind": "auth_success"},
                        {"actor_id": "token-invalid-01", "kind": "auth_fail"},
                        {"actor_id": "token-valid-02", "kind": "auth_success"},
                    ],
                }
            ],
        },
    )

    monkeypatch.setattr(replay_abuse_regression_gate, "ROOT", repo)
    monkeypatch.setattr(replay_abuse_regression_gate, "CORPUS_PATH", corpus)
    monkeypatch.setattr(replay_abuse_regression_gate, "evidence_root", lambda: repo / "evidence")
    assert replay_abuse_regression_gate.main([]) == 0

    report = json.loads((repo / "evidence" / "security" / "replay_abuse_regression_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert "distributed_low_rate_evasion" in report["summary"]["scores"]
    assert "mixed_valid_invalid_token_spray" in report["summary"]["scores"]
    assert "deterministic_classifier_digest" in report["summary"]
    assert report["summary"]["classifier_outputs"]["distributed_low_rate_evasion"]["verdict"] == "normal"


def test_replay_abuse_regression_gate_fails_when_expected_classifier_drift_detected(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    corpus = repo / "artifacts" / "inputs" / "security" / "replay_abuse_regression_corpus.json"
    _write(
        corpus,
        {
            "schema_version": 1,
            "cases": [
                {
                    "name": "distributed_low_rate_evasion",
                    "expected_classifier": {
                        "verdict": "normal",
                        "reason_code": "low_signal",
                        "score": 0,
                    },
                    "events": [
                        {"actor_id": "actor-01", "kind": "replay"},
                        {"actor_id": "actor-02", "kind": "replay"},
                        {"actor_id": "actor-03", "kind": "replay"},
                        {"actor_id": "actor-04", "kind": "replay"},
                        {"actor_id": "actor-05", "kind": "replay"},
                        {"actor_id": "actor-06", "kind": "replay"},
                    ],
                }
            ],
        },
    )

    monkeypatch.setattr(replay_abuse_regression_gate, "ROOT", repo)
    monkeypatch.setattr(replay_abuse_regression_gate, "CORPUS_PATH", corpus)
    monkeypatch.setattr(replay_abuse_regression_gate, "evidence_root", lambda: repo / "evidence")
    assert replay_abuse_regression_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "replay_abuse_regression_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("classifier_output_mismatch:distributed_low_rate_evasion:") for item in report["findings"])


def test_replay_abuse_regression_gate_flags_low_and_slow_distributed_replay_as_anomalous(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    corpus = repo / "artifacts" / "inputs" / "security" / "replay_abuse_regression_corpus.json"
    _write(
        corpus,
        {
            "schema_version": 1,
            "cases": [
                {
                    "name": "distributed_low_rate_evasion",
                    "expected_classifier": {
                        "verdict": "anomalous_high",
                        "reason_code": "distributed_actor_spray",
                        "score": 24,
                    },
                    "events": [
                        {"actor_id": "actor-01", "kind": "replay"},
                        {"actor_id": "actor-02", "kind": "replay"},
                        {"actor_id": "actor-03", "kind": "replay"},
                        {"actor_id": "actor-04", "kind": "replay"},
                        {"actor_id": "actor-05", "kind": "replay"},
                        {"actor_id": "actor-06", "kind": "replay"},
                    ],
                }
            ],
        },
    )
    monkeypatch.setattr(replay_abuse_regression_gate, "ROOT", repo)
    monkeypatch.setattr(replay_abuse_regression_gate, "CORPUS_PATH", corpus)
    monkeypatch.setattr(replay_abuse_regression_gate, "evidence_root", lambda: repo / "evidence")
    assert replay_abuse_regression_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "replay_abuse_regression_gate.json").read_text(encoding="utf-8"))
    observed = report["summary"]["classifier_outputs"]["distributed_low_rate_evasion"]
    assert observed["verdict"] == "anomalous_high"
    assert observed["reason_code"] == "distributed_actor_spray"
    assert observed["score"] == 24
