#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

HISTORY_PATH = ROOT / "evidence" / "security" / "gate_status_transition_history.json"
CHRONIC_NON_PASS_THRESHOLD = 3
MAX_HISTORY = 20


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _gate_status_map(sec: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in sorted(sec.glob("*.json")):
        name = path.name
        if name in {
            "gate_status_transition_history.json",
            "gate_status_transition_anomaly_detector.json",
        }:
            continue
        try:
            payload = _load_json(path)
        except Exception:
            continue
        status = str(payload.get("status", "UNKNOWN")).strip().upper() or "UNKNOWN"
        statuses[name] = status
    return statuses


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    anomalies: list[dict[str, Any]] = []

    if HISTORY_PATH.exists():
        try:
            history_doc = _load_json(HISTORY_PATH)
        except Exception:
            history_doc = {}
            findings.append("invalid_status_transition_history")
    else:
        history_doc = {}

    history = history_doc.get("history", {}) if isinstance(history_doc, dict) else {}
    if not isinstance(history, dict):
        history = {}

    current = _gate_status_map(sec)
    updated: dict[str, list[str]] = {}

    for gate_name, current_status in current.items():
        prior = history.get(gate_name, [])
        if not isinstance(prior, list):
            prior = []
        prior_statuses = [str(x).upper() for x in prior if isinstance(x, str)]

        tail = prior_statuses[-CHRONIC_NON_PASS_THRESHOLD:]
        chronic_non_pass = len(tail) == CHRONIC_NON_PASS_THRESHOLD and all(x in {"FAIL", "WARN"} for x in tail)
        if chronic_non_pass and current_status == "PASS":
            anomalies.append(
                {
                    "gate": gate_name,
                    "transition": "chronic_non_pass_to_pass",
                    "prior_tail": tail,
                    "current": current_status,
                }
            )
            findings.append(f"suspicious_recovery_transition:{gate_name}")

        new_hist = (prior_statuses + [current_status])[-MAX_HISTORY:]
        updated[gate_name] = new_hist

    for gate_name, prior in history.items():
        if gate_name in updated:
            continue
        if isinstance(prior, list):
            updated[gate_name] = [str(x).upper() for x in prior if isinstance(x, str)][-MAX_HISTORY:]

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at_utc": datetime.now(UTC).isoformat(),
                "history": updated,
                "chronic_non_pass_threshold": CHRONIC_NON_PASS_THRESHOLD,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report = {
        "status": "PASS" if not findings else "WARN",
        "findings": findings,
        "summary": {
            "gates_observed": len(current),
            "anomalies_detected": len(anomalies),
            "chronic_non_pass_threshold": CHRONIC_NON_PASS_THRESHOLD,
            "history_path": str(HISTORY_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "gate_status_transition_anomaly_detector"},
        "anomalies": anomalies,
    }
    out = sec / "gate_status_transition_anomaly_detector.json"
    write_json_report(out, report)
    print(f"GATE_STATUS_TRANSITION_ANOMALY_DETECTOR: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
