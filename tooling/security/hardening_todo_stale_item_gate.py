#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_TODO = ""
UPDATED_RE = re.compile(r"\bupdated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}(?:[T ][^ \t]+)?)", re.IGNORECASE)
SLA_POLICY = ROOT / "governance" / "security" / "hardening_backlog_sla_policy.json"


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        try:
            dt = datetime.fromisoformat(fixed.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


def _parse_updated(raw: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(raw.replace(" ", "T").replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _load_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_policy(SLA_POLICY)
    policy_todo = str(policy.get("todo_path", DEFAULT_TODO)).strip() if isinstance(policy, dict) else DEFAULT_TODO
    configured = os.environ.get("GLYPHSER_HARDENING_TODO_PATH", policy_todo).strip()
    todo_path = (ROOT / configured).resolve() if configured and not configured.startswith("/") else Path(configured).expanduser()
    default_sla_days = int(policy.get("sla_days", 45)) if isinstance(policy.get("sla_days", 45), (int, float)) else 45
    sla_days = int(os.environ.get("GLYPHSER_HARDENING_ITEM_SLA_DAYS", str(default_sla_days)) or str(default_sla_days))
    policy_require_updated = bool(policy.get("require_updated_tag", False)) if isinstance(policy, dict) else False
    require_updated = _to_bool(os.environ.get("GLYPHSER_HARDENING_REQUIRE_UPDATED_TAG", str(policy_require_updated)))

    findings: list[str] = []
    skipped = False
    stale_count = 0
    missing_updated_count = 0
    checked_items = 0
    now = _now_utc()

    if not configured or not todo_path.exists():
        skipped = True
    else:
        for idx, line in enumerate(todo_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not (stripped.startswith("[ ]") or stripped.startswith("[~]")):
                continue
            checked_items += 1
            match = UPDATED_RE.search(stripped)
            if not match:
                missing_updated_count += 1
                if require_updated:
                    findings.append(f"missing_updated_tag:line:{idx}")
                continue
            updated = _parse_updated(match.group(1))
            if updated is None:
                findings.append(f"invalid_updated_tag:line:{idx}")
                continue
            age = now - updated
            if age > timedelta(days=sla_days):
                stale_count += 1
                findings.append(f"stale_item:line:{idx}:age_days:{age.days}:sla_days:{sla_days}")

    report = {
        "status": "PASS" if skipped or not findings else "FAIL",
        "skipped": skipped,
        "findings": findings,
        "summary": {
            "todo_path": str(todo_path) if configured else "",
            "checked_items": checked_items,
            "stale_items": stale_count,
            "missing_updated_tags": missing_updated_count,
            "sla_days": sla_days,
            "require_updated_tag": require_updated,
            "now_utc": now.isoformat(),
            "sla_policy_path": str(SLA_POLICY),
        },
        "metadata": {"gate": "hardening_todo_stale_item_gate"},
    }
    out = evidence_root() / "security" / "hardening_todo_stale_item_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_TODO_STALE_ITEM_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
