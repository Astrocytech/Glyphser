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

SEVERE_KEYWORDS = (
    "tamper",
    "signature_invalid",
    "signature_mismatch",
    "corruption",
    "critical",
    "compromised",
    "policy_signature",
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _recommendations_for_signal(signal: str) -> list[str]:
    low = signal.lower()
    recs = ["Escalate to security incident channel and preserve affected evidence artifacts."]
    if "signature" in low or "policy_signature" in low:
        recs.append("Temporarily block release/promotion workflows pending signature integrity verification.")
    if "tamper" in low or "corruption" in low:
        recs.append("Trigger evidence chain-of-custody verify and archive integrity revalidation immediately.")
    if "compromised" in low:
        recs.append("Trigger compromised runner drill and rotate affected credentials/keys.")
    return recs


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    severe_signals: list[dict[str, Any]] = []
    findings: list[str] = []

    for path in sorted(sec.glob("*.json")):
        if path.name == "containment_auto_trigger_recommendations.json":
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
            low = text.lower()
            if text and any(token in low for token in SEVERE_KEYWORDS):
                severe_signals.append(
                    {
                        "source_report": path.name,
                        "finding": text,
                        "recommended_actions": _recommendations_for_signal(text),
                    }
                )
                findings.append(f"severe_signal_detected:{path.name}:{text}")

    report = {
        "status": "PASS" if not severe_signals else "WARN",
        "findings": findings,
        "summary": {
            "severe_signals": len(severe_signals),
            "auto_trigger_recommendations": sum(len(item.get("recommended_actions", [])) for item in severe_signals),
        },
        "metadata": {"gate": "containment_auto_trigger_recommendations"},
        "recommendations": severe_signals,
    }

    out = sec / "containment_auto_trigger_recommendations.json"
    write_json_report(out, report)
    print(f"CONTAINMENT_AUTO_TRIGGER_RECOMMENDATIONS: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
