#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RUBRIC = {
    "critical": {
        "score": 100,
        "keywords": ["compromised", "key_leak", "critical", "active_exploit"],
    },
    "high": {
        "score": 80,
        "keywords": ["tamper", "signature_invalid", "signature_mismatch", "corruption"],
    },
    "medium": {
        "score": 50,
        "keywords": ["warn", "unexpected", "drift", "stale"],
    },
    "low": {
        "score": 20,
        "keywords": ["info", "advisory"],
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _classify(finding: str) -> tuple[str, int]:
    low = finding.lower()
    for level in ("critical", "high", "medium", "low"):
        data = RUBRIC[level]
        if any(keyword in low for keyword in data["keywords"]):
            return level.upper(), int(data["score"])
    return "LOW", int(RUBRIC["low"]["score"])


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    scored: list[dict[str, Any]] = []
    max_score = 0

    for path in sorted(sec.glob("*.json")):
        if path.name == "incident_severity_scoring_report.json":
            continue
        try:
            payload = _load_json(path)
        except Exception:
            continue
        raw_findings = payload.get("findings", []) if isinstance(payload, dict) else []
        if not isinstance(raw_findings, list):
            continue
        for finding in raw_findings:
            text = str(finding).strip()
            if not text:
                continue
            severity, score = _classify(text)
            max_score = max(max_score, score)
            scored.append(
                {
                    "source_report": path.name,
                    "finding": text,
                    "severity": severity,
                    "score": score,
                }
            )

    scored.sort(key=lambda row: int(row.get("score", 0)), reverse=True)
    if max_score >= 80:
        status = "WARN"
    else:
        status = "PASS"

    report = {
        "status": status,
        "findings": [],
        "summary": {
            "scored_findings": len(scored),
            "max_severity_score": max_score,
            "critical_or_high_findings": sum(1 for row in scored if int(row.get("score", 0)) >= 80),
        },
        "metadata": {"gate": "incident_severity_scoring_report"},
        "severity_rubric": RUBRIC,
        "scored_findings": scored,
    }
    out = sec / "incident_severity_scoring_report.json"
    write_json_report(out, report)
    print(f"INCIDENT_SEVERITY_SCORING_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
