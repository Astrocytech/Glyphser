from __future__ import annotations

import json
from pathlib import Path

from tooling.security import secret_origin_inventory_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_secret_origin_inventory_gate_passes_with_recertified_required_secrets(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    inv = repo / "governance" / "security" / "secret_origin_inventory.json"
    sec_policy = repo / "governance" / "security" / "secret_management_policy.json"
    org_policy = repo / "governance" / "security" / "org_secret_backend_policy.json"

    _write(sec_policy, {"required_secrets": ["A", "B"]})
    _write(org_policy, {"required_secrets": ["B", "C"]})
    _write(
        inv,
        {
            "maximum_recertification_age_days": 3650,
            "secrets": [
                {
                    "name": "A",
                    "provisioned_by": "alice",
                    "provisioning_source": "vault",
                    "provisioning_method": "automated",
                    "last_recertified_utc": "2026-03-01T00:00:00Z",
                    "recertification_interval_days": 3650,
                },
                {
                    "name": "B",
                    "provisioned_by": "bob",
                    "provisioning_source": "vault",
                    "provisioning_method": "manual",
                    "last_recertified_utc": "2026-03-01T00:00:00Z",
                    "recertification_interval_days": 3650,
                },
                {
                    "name": "C",
                    "provisioned_by": "carol",
                    "provisioning_source": "vault",
                    "provisioning_method": "manual",
                    "last_recertified_utc": "2026-03-01T00:00:00Z",
                    "recertification_interval_days": 3650,
                },
            ],
        },
    )

    monkeypatch.setattr(secret_origin_inventory_gate, "ROOT", repo)
    monkeypatch.setattr(secret_origin_inventory_gate, "INVENTORY", inv)
    monkeypatch.setattr(secret_origin_inventory_gate, "SECRET_POLICY", sec_policy)
    monkeypatch.setattr(secret_origin_inventory_gate, "ORG_POLICY", org_policy)
    monkeypatch.setattr(secret_origin_inventory_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_origin_inventory_gate.main([]) == 0


def test_secret_origin_inventory_gate_fails_when_required_secret_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    inv = repo / "governance" / "security" / "secret_origin_inventory.json"
    sec_policy = repo / "governance" / "security" / "secret_management_policy.json"
    org_policy = repo / "governance" / "security" / "org_secret_backend_policy.json"

    _write(sec_policy, {"required_secrets": ["A"]})
    _write(org_policy, {"required_secrets": []})
    _write(
        inv,
        {
            "maximum_recertification_age_days": 3650,
            "secrets": [
                {
                    "name": "B",
                    "provisioned_by": "bob",
                    "provisioning_source": "vault",
                    "provisioning_method": "manual",
                    "last_recertified_utc": "2026-03-01T00:00:00Z",
                    "recertification_interval_days": 3650,
                }
            ],
        },
    )

    monkeypatch.setattr(secret_origin_inventory_gate, "ROOT", repo)
    monkeypatch.setattr(secret_origin_inventory_gate, "INVENTORY", inv)
    monkeypatch.setattr(secret_origin_inventory_gate, "SECRET_POLICY", sec_policy)
    monkeypatch.setattr(secret_origin_inventory_gate, "ORG_POLICY", org_policy)
    monkeypatch.setattr(secret_origin_inventory_gate, "evidence_root", lambda: repo / "evidence")
    assert secret_origin_inventory_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "secret_origin_inventory_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_required_secret_inventory:") for item in report["findings"])
