from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import network_endpoint_documentation_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_network_endpoint_documentation_gate_passes_when_endpoints_are_documented(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "network_endpoint_inventory.json"
    script = repo / "tooling" / "security" / "sample_gate.py"
    security_policy = repo / "governance" / "security" / "network_egress_policy.json"
    _write_json(policy, {"documented_endpoints": ["api.github.com", "pypi.org"]})
    _sign(policy)
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text('URL = "https://api.github.com/repos/org/repo"\n', encoding="utf-8")
    _write_json(security_policy, {"allowed_egress_domains": ["pypi.org"]})

    monkeypatch.setattr(network_endpoint_documentation_gate, "ROOT", repo)
    monkeypatch.setattr(network_endpoint_documentation_gate, "POLICY", policy)
    monkeypatch.setattr(network_endpoint_documentation_gate, "evidence_root", lambda: repo / "evidence")
    assert network_endpoint_documentation_gate.main([]) == 0


def test_network_endpoint_documentation_gate_fails_for_undocumented_endpoint(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "network_endpoint_inventory.json"
    script = repo / "tooling" / "security" / "sample_gate.py"
    _write_json(policy, {"documented_endpoints": ["pypi.org"]})
    _sign(policy)
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text('URL = "https://api.github.com/repos/org/repo"\n', encoding="utf-8")

    monkeypatch.setattr(network_endpoint_documentation_gate, "ROOT", repo)
    monkeypatch.setattr(network_endpoint_documentation_gate, "POLICY", policy)
    monkeypatch.setattr(network_endpoint_documentation_gate, "evidence_root", lambda: repo / "evidence")
    assert network_endpoint_documentation_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "network_endpoint_documentation_gate.json").read_text(encoding="utf-8")
    )
    assert any(str(item).startswith("undocumented_network_endpoint:") for item in report["findings"])
