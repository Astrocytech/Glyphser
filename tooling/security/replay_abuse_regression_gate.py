#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Any, Mapping

CASES = [
    {
        "name": "single_actor_burst",
        "events": [{"actor_id": "actor-01", "kind": "replay"}] * 8,
        "expected_classifier": {
            "verdict": "normal",
            "reason_code": "single_actor_burst",
            "score": 11,
        },
    },
    {
        "name": "actor_spray",
        "events": [{"actor_id": f"actor-{i:02d}", "kind": "replay"} for i in range(8)],
        "expected_classifier": {
            "verdict": "anomalous_high",
            "reason_code": "distributed_actor_spray",
            "score": 32,
        },
    },
]
ANOMALOUS_SCORE_THRESHOLD = 20


def _score(case: Mapping[str, object]) -> int:
    events = case.get("events", [])
    if not isinstance(events, list):
        return -1
    actors = [str(e.get("actor_id", "")) for e in events if isinstance(e, dict)]
    unique = len(set(actors))
    return len(actors) + (unique * 3)


def _classify(case: Mapping[str, object], score: int) -> dict[str, object]:
    events = case.get("events", [])
    if not isinstance(events, list):
        return {"verdict": "invalid", "reason_code": "invalid_events", "score": score}
    actors = [str(e.get("actor_id", "")) for e in events if isinstance(e, dict)]
    unique = len(set(actors))
    if score >= 24:
        verdict = "anomalous_high"
    elif score >= 14:
        verdict = "anomalous_medium"
    else:
        verdict = "normal"
    if unique >= max(4, len(events) // 2):
        reason_code = "distributed_actor_spray"
    elif len(events) >= 6:
        reason_code = "single_actor_burst"
    else:
        reason_code = "low_signal"
    return {"verdict": verdict, "reason_code": reason_code, "score": score}


def _python_version() -> str:
    return platform.python_version()


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CORPUS_PATH = ROOT / "artifacts" / "inputs" / "security" / "replay_abuse_regression_corpus.json"

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load_external_cases() -> list[dict[str, object]]:
    if not CORPUS_PATH.exists():
        return []
    try:
        payload = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    raw_cases = payload.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    cases: list[dict[str, object]] = []
    for item in raw_cases:
        if isinstance(item, dict):
            cases.append(item)
    return cases


def _stable_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scores: dict[str, int] = {}
    classifier_outputs: dict[str, dict[str, object]] = {}
    all_cases = CASES + _load_external_cases()
    for case in all_cases:
        name = str(case["name"])
        score = _score(case)
        if score < 0:
            findings.append(f"invalid_case:{name}")
            continue
        scores[name] = score
        observed = _classify(case, score)
        classifier_outputs[name] = observed
        expected = case.get("expected_classifier")
        if score >= ANOMALOUS_SCORE_THRESHOLD and not isinstance(expected, dict):
            findings.append(f"missing_expected_classifier_for_anomalous_case:{name}")
        if isinstance(expected, dict):
            expected_payload = {
                "verdict": str(expected.get("verdict", "")).strip(),
                "reason_code": str(expected.get("reason_code", "")).strip(),
                "score": int(expected.get("score", -1)),
            }
            if expected_payload != observed:
                findings.append(
                    f"classifier_output_mismatch:{name}:expected={_stable_digest(expected_payload)}:observed={_stable_digest(observed)}"
                )

    digest = hashlib.sha256(json.dumps(scores, sort_keys=True).encode("utf-8")).hexdigest()
    classifier_digest = _stable_digest(classifier_outputs)
    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "scores": scores,
            "classifier_outputs": classifier_outputs,
            "deterministic_digest": digest,
            "deterministic_classifier_digest": classifier_digest,
            "anomalous_score_threshold": ANOMALOUS_SCORE_THRESHOLD,
            "corpus_path": str(CORPUS_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "replay_abuse_regression_gate", "python_version": _python_version()},
    }
    out = evidence_root() / "security" / "replay_abuse_regression_gate.json"
    write_json_report(out, report)
    print(f"REPLAY_ABUSE_REGRESSION_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
