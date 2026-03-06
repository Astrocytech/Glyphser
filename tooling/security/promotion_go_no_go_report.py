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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "promotion_go_no_go_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _status_score(status: str) -> float:
    s = status.upper()
    if s == "PASS":
        return 1.0
    if s == "WARN":
        return 0.5
    return 0.0


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_promotion_go_no_go_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    controls = policy.get("controls", []) if isinstance(policy, dict) else []
    min_score = float(policy.get("minimum_weighted_score", 80.0) or 80.0) if isinstance(policy, dict) else 80.0
    warn_thresholds_all = policy.get("warn_thresholds_by_env", {}) if isinstance(policy, dict) else {}
    if not isinstance(warn_thresholds_all, dict):
        warn_thresholds_all = {}
    env_name = os.environ.get("GLYPHSER_DEPLOY_ENV", "ci").strip().lower() or "ci"
    warn_thresholds_raw = warn_thresholds_all.get(env_name, {})
    if not isinstance(warn_thresholds_raw, dict):
        warn_thresholds_raw = {}
    warn_thresholds = {str(k).strip(): int(v) for k, v in warn_thresholds_raw.items() if str(k).strip()}
    if not isinstance(controls, list):
        controls = []
        findings.append("invalid_controls_list")

    details: list[dict[str, Any]] = []
    weighted_total = 0.0
    weight_sum = 0.0
    blockers: list[str] = []
    promotion_blockers: list[dict[str, Any]] = []
    warning_category_counts: dict[str, int] = {}

    for item in controls:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip() or "unnamed_control"
        rel = str(item.get("report_path", "")).strip()
        weight = float(item.get("weight", 0) or 0)
        mandatory = bool(item.get("mandatory", False))

        report_status = "MISSING"
        if rel:
            path = ROOT / rel
            if path.exists():
                payload = _load_json(path)
                report_status = str(payload.get("status", "UNKNOWN")).upper()
                warn_cats = payload.get("warning_categories", {})
                if isinstance(warn_cats, dict):
                    for key, value in warn_cats.items():
                        category = str(key).strip()
                        if not category:
                            continue
                        try:
                            count = int(value)
                        except Exception:
                            continue
                        warning_category_counts[category] = warning_category_counts.get(category, 0) + max(count, 0)
            else:
                report_status = "MISSING"
        else:
            findings.append(f"missing_report_path:{name}")

        contribution = _status_score(report_status) * max(weight, 0.0)
        weighted_total += contribution
        weight_sum += max(weight, 0.0)

        if mandatory and report_status != "PASS":
            blocker = f"mandatory_control_not_pass:{name}:{report_status}"
            blockers.append(blocker)
            promotion_blockers.append(
                {
                    "class": "mandatory_control_not_pass",
                    "control": name,
                    "status": report_status,
                    "report_path": rel,
                }
            )
        if env_name in {"release", "prod"} and report_status == "WARN":
            blocker = f"release_warn_not_allowed:{name}"
            blockers.append(blocker)
            promotion_blockers.append(
                {
                    "class": "release_warn_not_allowed",
                    "control": name,
                    "status": report_status,
                    "report_path": rel,
                }
            )

        details.append(
            {
                "name": name,
                "report_path": rel,
                "status": report_status,
                "weight": weight,
                "mandatory": mandatory,
                "score_contribution": round(contribution, 2),
            }
        )

    weighted_score = 100.0 if weight_sum <= 0 else round((weighted_total / weight_sum) * 100.0, 2)
    findings.extend(blockers)
    if weighted_score < min_score:
        findings.append(f"weighted_score_below_threshold:{weighted_score}:{min_score}")
        promotion_blockers.append(
            {
                "class": "weighted_score_below_threshold",
                "weighted_score": weighted_score,
                "minimum_weighted_score": min_score,
            }
        )
    for category, count in sorted(warning_category_counts.items()):
        allowed = int(warn_thresholds.get(category, 0))
        if count > allowed:
            findings.append(f"warn_threshold_exceeded:{env_name}:{category}:{count}:{allowed}")
            promotion_blockers.append(
                {
                    "class": "warn_threshold_exceeded",
                    "environment": env_name,
                    "category": category,
                    "count": count,
                    "allowed": allowed,
                }
            )

    decision = "GO" if not blockers and weighted_score >= min_score and not findings else "NO_GO"
    status = "PASS" if decision == "GO" else "FAIL"

    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "decision": decision,
            "weighted_score": weighted_score,
            "minimum_weighted_score": min_score,
            "mandatory_blockers": len(blockers),
            "controls_evaluated": len(details),
            "environment": env_name,
            "warn_thresholds": warn_thresholds,
            "warning_category_counts": warning_category_counts,
            "promotion_blockers": promotion_blockers,
            "promotion_blocker_count": len(promotion_blockers),
        },
        "metadata": {"gate": "promotion_go_no_go_report"},
        "controls": details,
    }

    out = evidence_root() / "security" / "promotion_go_no_go_report.json"
    write_json_report(out, report)
    print(f"PROMOTION_GO_NO_GO_REPORT: {report['status']} ({decision})")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
