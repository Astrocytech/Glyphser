#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

DEFAULT_REGISTRY = ROOT / "governance" / "security" / "hardening_ticket_registry.json"
DEFAULT_POLICY = ROOT / "governance" / "security" / "hardening_ticket_risk_scoring_policy.json"
_CLOSED_STATES = {"DONE", "CLOSED", "RESOLVED"}


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    parsed = _parse_ts(fixed) if fixed else None
    return parsed or datetime.now(UTC)


def _load_tickets(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_ticket_registry"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_ticket_registry_json"
    if isinstance(payload, dict):
        raw = payload.get("tickets", [])
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)], ""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], ""
    return [], "invalid_ticket_registry_schema"


def _load_policy(path: Path) -> tuple[dict[str, Any], str]:
    defaults: dict[str, Any] = {
        "top_n": 10,
        "weights": {
            "severity": 3.0,
            "exploitability": 2.0,
            "blast_radius": 2.0,
            "overdue_days": 1.5,
            "age_days": 0.5,
        },
    }
    if not path.exists():
        return defaults, "missing_risk_scoring_policy"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return defaults, "invalid_risk_scoring_policy_json"
    if not isinstance(payload, dict):
        return defaults, "invalid_risk_scoring_policy_schema"
    merged = dict(defaults)
    merged.update({k: v for k, v in payload.items() if k in {"top_n", "weights"}})
    return merged, ""


def _num(value: object, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return fallback


def _score_ticket(
    ticket: dict[str, Any],
    *,
    now: datetime,
    weights: dict[str, float],
) -> tuple[dict[str, Any], str]:
    ticket_id = str(ticket.get("ticket_id", "")).strip().upper()
    if not ticket_id:
        return {}, "missing_ticket_id"
    state = str(ticket.get("state", "OPEN")).strip().upper()
    if state in _CLOSED_STATES:
        return {}, ""

    created_at = _parse_ts(ticket.get("created_at_utc"))
    due_at = _parse_ts(ticket.get("due_at_utc"))
    severity = max(1.0, min(5.0, _num(ticket.get("severity"), 3.0)))
    exploitability = max(1.0, min(5.0, _num(ticket.get("exploitability"), 3.0)))
    blast_radius = max(1.0, min(5.0, _num(ticket.get("blast_radius"), 3.0)))
    overdue_days = 0.0
    if due_at is not None and due_at < now:
        overdue_days = (now - due_at).total_seconds() / 86400.0
    age_days = 0.0
    if created_at is not None and created_at < now:
        age_days = (now - created_at).total_seconds() / 86400.0

    weighted_score = (
        severity * weights.get("severity", 3.0)
        + exploitability * weights.get("exploitability", 2.0)
        + blast_radius * weights.get("blast_radius", 2.0)
        + min(overdue_days, 180.0) / 30.0 * weights.get("overdue_days", 1.5)
        + min(age_days, 365.0) / 30.0 * weights.get("age_days", 0.5)
    )
    confidence = "high"
    if not str(ticket.get("owner", "")).strip() or due_at is None:
        confidence = "medium"
    if created_at is None:
        confidence = "low"

    ranked = {
        "ticket_id": ticket_id,
        "title": str(ticket.get("title", "")).strip(),
        "owner": str(ticket.get("owner", "")).strip(),
        "eta_utc": due_at.isoformat() if due_at else "",
        "confidence": confidence,
        "state": state,
        "severity": round(severity, 3),
        "exploitability": round(exploitability, 3),
        "blast_radius": round(blast_radius, 3),
        "due_at_utc": due_at.isoformat() if due_at else "",
        "created_at_utc": created_at.isoformat() if created_at else "",
        "overdue_days": round(overdue_days, 3),
        "age_days": round(age_days, 3),
        "weighted_risk_score": round(weighted_score, 4),
    }
    return ranked, ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    now = _now_utc()
    registry_path = Path(os.environ.get("GLYPHSER_HARDENING_TICKET_STATE_PATH", str(DEFAULT_REGISTRY))).expanduser()
    policy_path = Path(os.environ.get("GLYPHSER_HARDENING_RISK_POLICY_PATH", str(DEFAULT_POLICY))).expanduser()

    tickets, ticket_err = _load_tickets(registry_path)
    if ticket_err:
        findings.append(ticket_err)
    policy, policy_err = _load_policy(policy_path)
    if policy_err:
        findings.append(policy_err)

    weights_cfg = policy.get("weights", {}) if isinstance(policy, dict) else {}
    weights = {k: _num(v, 0.0) for k, v in (weights_cfg.items() if isinstance(weights_cfg, dict) else [])}
    top_n_raw = policy.get("top_n", 10) if isinstance(policy, dict) else 10
    top_n = max(1, int(_num(top_n_raw, 10.0)))

    ranked_items: list[dict[str, Any]] = []
    for ticket in tickets:
        ranked, row_err = _score_ticket(ticket, now=now, weights=weights)
        if row_err:
            findings.append(row_err)
            continue
        if ranked:
            ranked_items.append(ranked)
    ranked_items.sort(
        key=lambda item: (-float(item["weighted_risk_score"]), -float(item["overdue_days"]), str(item["ticket_id"]))
    )
    top = ranked_items[:top_n]

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "ticket_registry_path": str(registry_path),
            "risk_policy_path": str(policy_path),
            "total_tickets": len(tickets),
            "unresolved_tickets": len(ranked_items),
            "ranked_items": len(top),
            "top_n": top_n,
            "evaluated_at_utc": now.isoformat(),
        },
        "weights": weights,
        "top_risk_unresolved_items": top,
        "metadata": {"gate": "top_risk_unresolved_items_ranker"},
    }
    out = evidence_root() / "security" / "top_risk_unresolved_items_ranker.json"
    write_json_report(out, report)
    print(f"TOP_RISK_UNRESOLVED_ITEMS_RANKER: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
