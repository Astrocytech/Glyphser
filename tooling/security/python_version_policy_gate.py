#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "python_version_policy.json"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
_VERSION_RE = re.compile(r"\b(3\.\d+)\b")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _discover_python_minors() -> dict[str, list[str]]:
    versions: dict[str, list[str]] = {}
    for wf in sorted(WORKFLOWS_DIR.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "python-version:" not in line:
                continue
            minors = sorted({match.group(1) for match in _VERSION_RE.finditer(line)})
            for minor in minors:
                versions.setdefault(minor, []).append(wf.name)
    return versions


def _parse_date(text: str) -> datetime | None:
    value = str(text).strip()
    if not value:
        return None
    try:
        if len(value) == 10:
            return datetime.fromisoformat(value + "T00:00:00+00:00")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    warnings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_python_version_policy")
        policy = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_python_version_policy")

    approved_raw = policy.get("approved_python_minors", []) if isinstance(policy, dict) else []
    approved = sorted({str(item).strip() for item in approved_raw if isinstance(item, str) and str(item).strip()})

    warn_before_days = 365
    try:
        candidate = int(policy.get("warn_before_eol_days", warn_before_days))
        if candidate > 0:
            warn_before_days = candidate
    except Exception:
        pass

    eol_raw = policy.get("minor_eol_dates_utc", {}) if isinstance(policy, dict) else {}
    eol_dates = eol_raw if isinstance(eol_raw, dict) else {}

    discovered = _discover_python_minors()

    for minor, files in discovered.items():
        if minor not in approved:
            findings.append(f"unapproved_python_minor:{minor}:files:{','.join(sorted(set(files)))}")

    now = datetime.now(UTC)
    eol_warnings: list[dict[str, Any]] = []
    for minor in sorted(set(approved) & set(discovered.keys())):
        eol = _parse_date(eol_dates.get(minor, ""))
        if eol is None:
            findings.append(f"missing_or_invalid_eol_date:{minor}")
            continue
        days_until_eol = int((eol - now).total_seconds() // 86400)
        if days_until_eol < 0:
            findings.append(f"python_minor_past_eol:{minor}:days:{days_until_eol}")
            continue
        if days_until_eol <= warn_before_days:
            warning = f"python_minor_eol_warning:{minor}:days:{days_until_eol}"
            warnings.append(warning)
            eol_warnings.append({"minor": minor, "days_until_eol": days_until_eol, "eol_utc": eol.isoformat()})

    status = "FAIL" if findings else ("WARN" if warnings else "PASS")
    report = {
        "status": status,
        "findings": findings + warnings,
        "summary": {
            "approved_python_minors": approved,
            "discovered_python_minors": sorted(discovered.keys()),
            "warn_before_eol_days": warn_before_days,
            "workflow_count": len({name for names in discovered.values() for name in names}),
            "eol_warning_count": len(eol_warnings),
        },
        "version_usage": {minor: sorted(set(files)) for minor, files in sorted(discovered.items())},
        "eol_warnings": eol_warnings,
        "metadata": {"gate": "python_version_policy_gate"},
    }
    out = evidence_root() / "security" / "python_version_policy_gate.json"
    write_json_report(out, report)
    print(f"PYTHON_VERSION_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
