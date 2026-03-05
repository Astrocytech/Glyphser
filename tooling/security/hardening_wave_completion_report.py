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

POLICY = ROOT / "governance" / "security" / "hardening_execution_waves.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _check(rule: dict[str, Any]) -> tuple[bool, str]:
    kind = str(rule.get("type", "")).strip()
    rel = str(rule.get("path", "")).strip()
    if not rel:
        return False, "missing_rule_path"
    path = ROOT / rel
    if kind == "file_exists":
        return path.exists(), f"missing_file:{rel}"
    if kind == "file_contains":
        snippet = str(rule.get("snippet", "")).strip()
        if not snippet:
            return False, f"missing_snippet:{rel}"
        if not path.exists():
            return False, f"missing_file:{rel}"
        return snippet in path.read_text(encoding="utf-8"), f"missing_snippet_match:{rel}"
    return False, f"unknown_rule_type:{kind or 'empty'}:{rel}"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    results: dict[str, str] = {}
    details: dict[str, list[str]] = {}

    if not POLICY.exists():
        findings.append("missing_hardening_execution_waves_policy")
        waves: dict[str, Any] = {}
    else:
        waves_payload = _load_json(POLICY)
        waves = waves_payload.get("waves", {}) if isinstance(waves_payload.get("waves", {}), dict) else {}

    for wave, config in waves.items():
        checks_raw = config.get("checks", []) if isinstance(config, dict) else []
        checks = [item for item in checks_raw if isinstance(item, dict)] if isinstance(checks_raw, list) else []
        unmet: list[str] = []
        for rule in checks:
            ok, problem = _check(rule)
            if not ok:
                unmet.append(problem)
        passed = not unmet
        results[str(wave)] = "PASS" if passed else "FAIL"
        details[str(wave)] = unmet
        if not passed:
            findings.append(f"incomplete_{wave}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "waves_total": len(results),
            "waves_passed": sum(1 for value in results.values() if value == "PASS"),
        },
        "metadata": {"report": "hardening_wave_completion_report"},
        "waves": results,
        "wave_unmet_checks": details,
    }
    out = evidence_root() / "security" / "hardening_wave_completion_report.json"
    write_json_report(out, report)
    print(f"HARDENING_WAVE_COMPLETION_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
