#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

EPOCHS = ROOT / "governance" / "security" / "key_rotation_epochs.json"
KEY_POLICY = ROOT / "governance" / "security" / "key_management_policy.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _key_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    meta = payload.get("metadata", {})
    if isinstance(meta, dict):
        kp = meta.get("key_provenance", {})
        if isinstance(kp, dict) and kp:
            return kp
    kp = payload.get("key_provenance", {})
    return kp if isinstance(kp, dict) else {}


def _key_mode(kp: dict[str, Any]) -> str:
    if bool(kp.get("fallback_used", False)):
        return "fallback"
    source = str(kp.get("source", "")).strip()
    if source:
        return source
    adapter = str(kp.get("adapter", "")).strip()
    if adapter:
        return adapter
    return "unknown"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    policy = _load(sec / "policy_signature.json")
    provenance = _load(sec / "provenance_signature.json")
    attestation = _load(sec / "evidence_attestation_index.json")
    findings: list[str] = []

    sources = {
        "policy_signature": _key_provenance(policy),
        "provenance_signature": _key_provenance(provenance),
        "evidence_attestation_index": _key_provenance(attestation),
    }

    missing = sorted(name for name, kp in sources.items() if not kp)
    for name in missing:
        findings.append(f"missing_key_provenance:{name}")

    key_ids = {str(kp.get("key_id", "")).strip() for kp in sources.values() if kp}
    key_ids.discard("")
    if len(key_ids) > 1:
        findings.append(f"key_id_mismatch:{','.join(sorted(key_ids))}")

    adapters = {str(kp.get("adapter", "")).strip() for kp in sources.values() if kp}
    adapters.discard("")
    if len(adapters) > 1:
        findings.append(f"adapter_mismatch:{','.join(sorted(adapters))}")

    fallback_users = sorted(
        name for name, kp in sources.items() if isinstance(kp, dict) and bool(kp.get("fallback_used", False))
    )
    if fallback_users:
        findings.append(f"fallback_signing_used:{','.join(fallback_users)}")

    key_modes = {name: _key_mode(kp) for name, kp in sources.items() if kp}
    policy = _load(KEY_POLICY)
    enforce_mode_match = bool(policy.get("enforce_sibling_key_mode_match", True))
    distinct_modes = sorted({mode for mode in key_modes.values() if mode})
    if enforce_mode_match and len(distinct_modes) > 1:
        findings.append(f"key_mode_mismatch:{','.join(distinct_modes)}")

    epochs_payload = _load(EPOCHS)
    raw_epochs = epochs_payload.get("epochs", []) if isinstance(epochs_payload, dict) else []
    epoch_rows = [row for row in raw_epochs if isinstance(row, dict)]
    epoch_key_ids: list[str] = []
    latest_epoch_id = ""
    latest_epoch_key_id = ""
    if epoch_rows:
        index: dict[str, dict[str, Any]] = {}
        for row in epoch_rows:
            epoch_id = str(row.get("epoch_id", "")).strip()
            key_id = str(row.get("key_id", "")).strip()
            if not epoch_id or not key_id:
                findings.append("invalid_epoch_entry")
                continue
            if epoch_id in index:
                findings.append(f"duplicate_epoch_id:{epoch_id}")
                continue
            index[epoch_id] = row
            epoch_key_ids.append(key_id)
        latest = epoch_rows[-1] if epoch_rows else {}
        latest_epoch_id = str(latest.get("epoch_id", "")).strip()
        latest_epoch_key_id = str(latest.get("key_id", "")).strip()
        for row in epoch_rows:
            epoch_id = str(row.get("epoch_id", "")).strip()
            prev_epoch = str(row.get("previous_epoch_id", "")).strip()
            prev_key = str(row.get("previous_key_id", "")).strip()
            if not prev_epoch:
                continue
            parent = index.get(prev_epoch)
            if parent is None:
                findings.append(f"missing_previous_epoch:{epoch_id}:{prev_epoch}")
                continue
            parent_key = str(parent.get("key_id", "")).strip()
            if prev_key and prev_key != parent_key:
                findings.append(f"epoch_previous_key_mismatch:{epoch_id}:{prev_key}!={parent_key}")
        if key_ids and latest_epoch_key_id and key_ids != {latest_epoch_key_id}:
            findings.append(f"key_id_not_latest_epoch:{','.join(sorted(key_ids))}:{latest_epoch_key_id}")
    else:
        findings.append("missing_rotation_epochs")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "sources": sorted(sources.keys()),
            "missing_sources": missing,
            "distinct_key_ids": sorted(key_ids),
            "distinct_adapters": sorted(adapters),
            "distinct_key_modes": distinct_modes,
            "fallback_sources": fallback_users,
            "enforce_sibling_key_mode_match": enforce_mode_match,
            "rotation_epoch_count": len(epoch_rows),
            "rotation_epoch_key_ids": sorted(set(epoch_key_ids)),
            "latest_rotation_epoch_id": latest_epoch_id,
            "latest_rotation_key_id": latest_epoch_key_id,
        },
        "metadata": {"gate": "key_provenance_continuity_gate"},
    }
    out = sec / "key_provenance_continuity_gate.json"
    write_json_report(out, report)
    print(f"KEY_PROVENANCE_CONTINUITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
