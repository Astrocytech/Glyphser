#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _validation_paths() -> tuple[Path, Path, Path]:
    from tooling.lib.path_config import evidence_root

    base = evidence_root() / "validation"
    return base, base / "runs", base / "scorecards"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    BASE, RUNS, SCORECARDS = _validation_paths()
    BASE.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    SCORECARDS.mkdir(parents=True, exist_ok=True)

    run_files = sorted(RUNS.glob("*.json"))
    runs = [_load_json(p) for p in run_files]

    issues_path = BASE / "issues.json"
    issues = _load_json(issues_path) if issues_path.exists() else {"issues": []}
    security_review = BASE / "external_security_review.md"

    missing = []
    if len(runs) < 3:
        missing.append("at_least_3_runs")
    if not security_review.exists():
        missing.append("external_security_review")

    unresolved_critical = [
        i for i in issues.get("issues", []) if i.get("severity") == "critical" and i.get("status") != "closed"
    ]

    successes = [r for r in runs if bool(r.get("success"))]
    failure_rate = 0.0 if not runs else (len(runs) - len(successes)) / len(runs)
    os_set = sorted({str(r.get("os", "")).strip() for r in runs if str(r.get("os", "")).strip()})
    profile_set = sorted(
        {str(r.get("runtime_profile", "")).strip() for r in runs if str(r.get("runtime_profile", "")).strip()}
    )
    blind_run_ok = any(bool(r.get("blind_run")) for r in runs)
    docs_only_ok = any(bool(r.get("docs_only")) for r in runs)
    negative_path_ok = all(bool(r.get("negative_path_pass")) for r in runs) if runs else False
    setup_values = [float(r.get("setup_minutes", 0.0)) for r in runs]
    setup_spread = (max(setup_values) - min(setup_values)) if setup_values else 0.0

    scorecard_files = sorted(SCORECARDS.glob("*.json"))
    scorecards = [_load_json(p) for p in scorecard_files]
    scorecard_ok = len(scorecards) >= len(runs) and len(runs) > 0
    avg_supportability = mean(float(s.get("supportability_score", 0.0)) for s in scorecards) if scorecards else 0.0

    checks = {
        "runs_count": len(runs) >= 3,
        "all_runs_success": len(runs) > 0 and len(successes) == len(runs),
        "failure_rate_budget": failure_rate <= 0.05,
        "os_diversity": len(os_set) >= 2,
        "profile_diversity": len(profile_set) >= 2,
        "blind_run": blind_run_ok,
        "docs_only_run": docs_only_ok,
        "negative_path": negative_path_ok,
        "setup_time_spread_budget": setup_spread <= 25.0,
        "scorecards_present": scorecard_ok,
        "supportability_threshold": avg_supportability >= 4.0,
        "no_unresolved_critical": len(unresolved_critical) == 0,
        "external_security_review_present": security_review.exists(),
        "missing_requirements": len(missing) == 0,
    }
    overall = all(checks.values())
    latest = {
        "status": "PASS" if overall else "FAIL",
        "checks": checks,
        "runs_total": len(runs),
        "runs_success": len(successes),
        "failure_rate": round(failure_rate, 4),
        "os_diversity": os_set,
        "runtime_profile_diversity": profile_set,
        "setup_time_spread_minutes": round(setup_spread, 2),
        "avg_supportability_score": round(avg_supportability, 2),
        "unresolved_critical_issues": unresolved_critical,
        "missing": missing,
    }
    _write_json(BASE / "latest.json", latest)
    _write_json(
        BASE / "independent_verification_summary.json",
        {
            "status": "PASS" if overall else "FAIL",
            "summary": "External validation completed with diversity, blind/docs-only, and negative-path checks."
            if overall
            else "External validation requirements not fully met.",
            "runs_total": len(runs),
            "runs_success": len(successes),
        },
    )
    if overall:
        print("EXTERNAL_VALIDATION_GATE: PASS")
        return 0
    print("EXTERNAL_VALIDATION_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
