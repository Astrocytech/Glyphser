#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

LOCALES = ("C.UTF-8", "en_US.UTF-8")
TARGET_GATES: list[tuple[str, str]] = [
    ("tooling/security/policy_schema_validation_gate.py", "policy_schema_validation_gate.json"),
    ("tooling/security/security_report_schema_contract_gate.py", "security_report_schema_contract_gate.json"),
    ("tooling/security/runtime_api_input_surface_gate.py", "runtime_api_input_surface_gate.json"),
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _normalized_report(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    findings = payload.get("findings", []) if isinstance(payload, dict) else []
    findings_list = sorted(str(item) for item in findings if isinstance(item, str)) if isinstance(findings, list) else []
    return {"status": str(payload.get("status", "")).strip(), "findings": findings_list}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    comparisons: dict[str, dict[str, Any]] = {}
    base_env = dict(os.environ)

    for script, report_name in TARGET_GATES:
        locale_results: dict[str, dict[str, Any]] = {}
        for locale in LOCALES:
            run_root = evidence_root().parent / f"locale-{locale.replace('.', '_').replace('-', '_')}"
            env = dict(base_env)
            env.update(
                {
                    "TZ": "UTC",
                    "LC_ALL": locale,
                    "LANG": locale,
                    "GLYPHSER_EVIDENCE_ROOT": str(run_root),
                }
            )
            proc = run_checked([sys.executable, script], cwd=ROOT, env=env)
            if proc.returncode != 0:
                findings.append(f"gate_failed_under_locale:{script}:{locale}:rc:{proc.returncode}")
                continue
            report_path = run_root / "security" / report_name
            if not report_path.exists():
                findings.append(f"missing_locale_report:{script}:{locale}:{report_name}")
                continue
            locale_results[locale] = _normalized_report(report_path)

        base = locale_results.get(LOCALES[0])
        compare = locale_results.get(LOCALES[1])
        if base is None or compare is None:
            continue
        matches = base == compare
        if not matches:
            findings.append(f"locale_behavior_drift:{script}")
        comparisons[script] = {
            "locales": locale_results,
            "matches": matches,
        }

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "locales": list(LOCALES),
            "gates_checked": len(TARGET_GATES),
            "gates_compared": len(comparisons),
            "mismatch_count": len([item for item in comparisons.values() if not item.get("matches", False)]),
        },
        "comparisons": comparisons,
        "metadata": {"gate": "locale_variance_suite"},
    }
    out = evidence_root() / "security" / "locale_variance_suite.json"
    write_json_report(out, report)
    print(f"LOCALE_VARIANCE_SUITE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
