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

HISTORY_PATH = ROOT / "evidence" / "security" / "cross_run_suspicious_pattern_history.json"
REPEAT_THRESHOLD = 2
KEYWORDS = (
    "tamper",
    "suspicious",
    "invalid_signature",
    "corruption",
    "recovery_transition",
    "unexpected_report_status",
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _collect_suspicious_signals(sec: Path) -> list[str]:
    signals: list[str] = []
    for path in sorted(sec.glob("*.json")):
        if path.name in {
            "cross_run_suspicious_pattern_linkage_gate.json",
            "cross_run_suspicious_pattern_history.json",
        }:
            continue
        try:
            payload = _load_json(path)
        except Exception:
            continue
        findings = payload.get("findings", []) if isinstance(payload, dict) else []
        if not isinstance(findings, list):
            continue
        for finding in findings:
            text = str(finding).strip()
            low = text.lower()
            if text and any(token in low for token in KEYWORDS):
                signals.append(f"{path.name}:{text}")
    return sorted(set(signals))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []

    if HISTORY_PATH.exists():
        try:
            history_doc = _load_json(HISTORY_PATH)
        except Exception:
            history_doc = {}
            findings.append("invalid_cross_run_suspicious_pattern_history")
    else:
        history_doc = {}

    counts = history_doc.get("counts", {}) if isinstance(history_doc, dict) else {}
    if not isinstance(counts, dict):
        counts = {}

    current_signals = _collect_suspicious_signals(sec)
    next_counts: dict[str, int] = {}
    for key, value in counts.items():
        if isinstance(key, str):
            try:
                next_counts[key] = int(value)
            except Exception:
                continue
    for signal in current_signals:
        next_counts[signal] = int(next_counts.get(signal, 0)) + 1

    linked_patterns = [
        {"signal": signal, "occurrences": next_counts.get(signal, 0)}
        for signal in sorted(current_signals)
        if int(next_counts.get(signal, 0)) >= REPEAT_THRESHOLD
    ]
    for item in linked_patterns:
        findings.append(f"repeated_suspicious_pattern:{item['signal']}:count:{item['occurrences']}")

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "updated_at_utc": datetime.now(UTC).isoformat(),
                "repeat_threshold": REPEAT_THRESHOLD,
                "counts": next_counts,
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
            "signals_this_run": len(current_signals),
            "linked_repeated_patterns": len(linked_patterns),
            "repeat_threshold": REPEAT_THRESHOLD,
            "history_path": str(HISTORY_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "cross_run_suspicious_pattern_linkage_gate"},
        "linked_patterns": linked_patterns,
    }
    out = sec / "cross_run_suspicious_pattern_linkage_gate.json"
    write_json_report(out, report)
    print(f"CROSS_RUN_SUSPICIOUS_PATTERN_LINKAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
