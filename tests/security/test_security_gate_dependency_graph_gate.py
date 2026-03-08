from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_dependency_graph_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_security_gate_dependency_graph_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)

    _write(
        sec / "security_super_gate_manifest.json",
        {
            "core": ["tooling/security/a_gate.py", "tooling/security/b_gate.py"],
            "extended": [],
        },
    )
    _write(
        gov / "security_gate_dependency_policy.json",
        {
            "dependencies": {"tooling/security/b_gate.py": ["tooling/security/a_gate.py"]},
            "critical_controls": [
                {
                    "control_id": "c1",
                    "verifiers": ["tooling/security/a_gate.py", "tooling/security/b_gate.py"],
                    "required_redundant_verifiers": 2,
                }
            ],
        },
    )

    monkeypatch.setattr(security_gate_dependency_graph_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_dependency_graph_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(
        security_gate_dependency_graph_gate,
        "POLICY",
        gov / "security_gate_dependency_policy.json",
    )
    monkeypatch.setattr(security_gate_dependency_graph_gate, "evidence_root", lambda: repo / "evidence")

    assert security_gate_dependency_graph_gate.main([]) == 0
    graph = json.loads((repo / "evidence" / "security" / "security_gate_dependency_graph.json").read_text(encoding="utf-8"))
    assert graph["dependencies"]["tooling/security/b_gate.py"] == ["tooling/security/a_gate.py"]


def test_security_gate_dependency_graph_gate_fails_on_cycle_and_spof(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)

    _write(
        sec / "security_super_gate_manifest.json",
        {
            "core": ["tooling/security/a_gate.py", "tooling/security/b_gate.py"],
            "extended": [],
        },
    )
    _write(
        gov / "security_gate_dependency_policy.json",
        {
            "dependencies": {
                "tooling/security/a_gate.py": ["tooling/security/b_gate.py"],
                "tooling/security/b_gate.py": ["tooling/security/a_gate.py"],
            },
            "critical_controls": [
                {
                    "control_id": "c1",
                    "verifiers": ["tooling/security/a_gate.py"],
                    "required_redundant_verifiers": 2,
                }
            ],
        },
    )

    monkeypatch.setattr(security_gate_dependency_graph_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_gate_dependency_graph_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(
        security_gate_dependency_graph_gate,
        "POLICY",
        gov / "security_gate_dependency_policy.json",
    )
    monkeypatch.setattr(security_gate_dependency_graph_gate, "evidence_root", lambda: repo / "evidence")

    assert security_gate_dependency_graph_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "security_gate_dependency_graph_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "FAIL"
    assert "single_point_of_failure:c1" in report["findings"]
    assert any(item.startswith("cyclic_dependency:") for item in report["findings"])
