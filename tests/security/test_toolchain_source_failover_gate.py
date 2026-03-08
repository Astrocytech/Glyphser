from __future__ import annotations

import json
from pathlib import Path

from tooling.security import toolchain_source_failover_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_toolchain_source_failover_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(repo / "governance" / "security" / "toolchain_source_failover_policy.json", {"primary_hosts": ["pypi.org"], "mirror_hosts": ["files.pythonhosted.org"]})
    _write_json(
        ev / "security" / "security_toolchain_install_report.json",
        {
            "install": [
                {
                    "metadata": {"name": "bandit"},
                    "download_info": {
                        "url": "https://files.pythonhosted.org/packages/bandit.whl",
                        "archive_info": {"hashes": {"sha256": "abc"}},
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_source_failover_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_source_failover_gate, "POLICY", repo / "governance" / "security" / "toolchain_source_failover_policy.json")
    monkeypatch.setattr(toolchain_source_failover_gate, "HISTORY", repo / "evidence" / "security" / "toolchain_source_failover_history.json")
    monkeypatch.setattr(toolchain_source_failover_gate, "evidence_root", lambda: ev)

    assert toolchain_source_failover_gate.main([]) == 0


def test_toolchain_source_failover_gate_fails_on_integrity_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(repo / "governance" / "security" / "toolchain_source_failover_policy.json", {"primary_hosts": ["pypi.org"], "mirror_hosts": ["files.pythonhosted.org"]})
    _write_json(
        ev / "security" / "security_toolchain_install_report.json",
        {
            "install": [
                {
                    "metadata": {"name": "bandit"},
                    "download_info": {
                        "url": "https://pypi.org/packages/bandit.whl",
                        "archive_info": {"hashes": {"sha256": "zzz"}},
                    },
                }
            ]
        },
    )
    _write_json(
        repo / "evidence" / "security" / "toolchain_source_failover_history.json",
        {"schema_version": 1, "packages": {"bandit": {"hashes": {"files.pythonhosted.org": "abc"}}}},
    )

    monkeypatch.setattr(toolchain_source_failover_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_source_failover_gate, "POLICY", repo / "governance" / "security" / "toolchain_source_failover_policy.json")
    monkeypatch.setattr(toolchain_source_failover_gate, "HISTORY", repo / "evidence" / "security" / "toolchain_source_failover_history.json")
    monkeypatch.setattr(toolchain_source_failover_gate, "evidence_root", lambda: ev)

    assert toolchain_source_failover_gate.main([]) == 1
    report = json.loads((ev / "security" / "toolchain_source_failover_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("integrity_equivalence_violation:bandit") for item in report["findings"])
