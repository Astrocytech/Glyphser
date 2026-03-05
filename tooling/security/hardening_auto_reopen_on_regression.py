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

REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_regression_detected(verification: dict[str, Any]) -> bool:
    if verification.get("regression_detected") is True:
        return True
    return bool(str(verification.get("regression_repro_ref", "")).strip())


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    reopened: list[str] = []

    if not REGISTRY.exists():
        findings.append("missing_hardening_pending_item_registry")
        entries: list[dict[str, Any]] = []
        payload: dict[str, Any] = {"entries": entries}
    else:
        payload = _load_json(REGISTRY)
        raw_entries = payload.get("entries", [])
        entries = [item for item in raw_entries if isinstance(item, dict)] if isinstance(raw_entries, list) else []

    changed = False
    for idx, row in enumerate(entries):
        status = str(row.get("status", "")).strip().lower()
        if status != "done":
            continue
        verification = row.get("verification", {}) if isinstance(row.get("verification"), dict) else {}
        if not _is_regression_detected(verification):
            continue

        item_id = str(row.get("id", f"idx-{idx}")).strip()
        row["previous_status"] = "done"
        row["status"] = "in_progress"
        row["reopen_reason"] = "regression_detected"
        if not str(row.get("negative_test_evidence_ref", "")).strip():
            row["negative_test_evidence_ref"] = str(verification.get("regression_repro_ref", "")).strip()
        reopened.append(item_id)
        changed = True

    if changed and REGISTRY.exists():
        payload["entries"] = entries
        _save_json(REGISTRY, payload)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"entries_checked": len(entries), "reopened_items": len(reopened)},
        "metadata": {"process": "hardening_auto_reopen_on_regression"},
        "reopened": reopened,
    }
    out = evidence_root() / "security" / "hardening_auto_reopen_on_regression.json"
    write_json_report(out, report)
    print(f"HARDENING_AUTO_REOPEN_ON_REGRESSION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
