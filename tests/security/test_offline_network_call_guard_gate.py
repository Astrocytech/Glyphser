from __future__ import annotations

import json
from pathlib import Path

from tooling.security import offline_network_call_guard_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_offline_network_call_guard_gate_passes_for_offline_script_without_network(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "network_egress_policy.json"
    sec_dir = repo / "tooling" / "security"
    _write_json(policy, {"network_required_gates": []})
    _write(sec_dir / "offline_verify.py", "def main():\n    return 0\n")

    monkeypatch.setattr(offline_network_call_guard_gate, "ROOT", repo)
    monkeypatch.setattr(offline_network_call_guard_gate, "POLICY", policy)
    monkeypatch.setattr(offline_network_call_guard_gate, "SECURITY_DIR", sec_dir)
    monkeypatch.setattr(offline_network_call_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert offline_network_call_guard_gate.main([]) == 0


def test_offline_network_call_guard_gate_fails_on_network_pattern(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "network_egress_policy.json"
    sec_dir = repo / "tooling" / "security"
    _write_json(policy, {"network_required_gates": []})
    _write(sec_dir / "offline_verify.py", "import requests\n")

    monkeypatch.setattr(offline_network_call_guard_gate, "ROOT", repo)
    monkeypatch.setattr(offline_network_call_guard_gate, "POLICY", policy)
    monkeypatch.setattr(offline_network_call_guard_gate, "SECURITY_DIR", sec_dir)
    monkeypatch.setattr(offline_network_call_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert offline_network_call_guard_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "offline_network_call_guard_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("offline_script_network_pattern:") for item in report["findings"])
