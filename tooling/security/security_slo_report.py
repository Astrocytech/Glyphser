#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load_policy() -> dict[str, object]:
    path = ROOT / "governance" / "security" / "security_observability_policy.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        p = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return p if isinstance(p, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    policy = _load_policy()
    target = float(policy.get("slo_target", 0.99))
    if target <= 0.0 or target >= 1.0:
        target = 0.99
    burn_rate_threshold = float(policy.get("burn_rate_alert_threshold", 2.0))
    if burn_rate_threshold < 0.0:
        burn_rate_threshold = 2.0
    gates = {
        "policy_signature": _load(sec / "policy_signature.json").get("status", "MISSING"),
        "provenance_signature": _load(sec / "provenance_signature.json").get("status", "MISSING"),
        "attestation": _load(sec / "evidence_attestation_gate.json").get("status", "MISSING"),
        "super_gate": _load(sec / "security_super_gate.json").get("status", "MISSING"),
    }
    pass_rate = sum(1 for v in gates.values() if str(v).upper() == "PASS") / max(1, len(gates))
    error_budget = 1.0 - target
    current_error_rate = max(0.0, 1.0 - pass_rate)
    burn_rate = current_error_rate / error_budget if error_budget > 0.0 else 0.0
    findings: list[str] = []
    if pass_rate < target:
        findings.append(f"security_slo_pass_rate_below_target:{pass_rate:.2%}")
    if burn_rate > burn_rate_threshold:
        findings.append(f"security_slo_burn_rate_above_threshold:{burn_rate:.3f}")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "pass_rate": pass_rate,
            "target": target,
            "burn_rate": burn_rate,
            "burn_rate_threshold": burn_rate_threshold,
            "gates": gates,
        },
        "metadata": {"gate": "security_slo_report"},
    }
    out = sec / "security_slo_report.json"
    write_json_report(out, report)
    print(f"SECURITY_SLO_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
