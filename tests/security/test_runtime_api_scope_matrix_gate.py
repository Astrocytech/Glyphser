from __future__ import annotations

import json
from pathlib import Path

from tooling.security import runtime_api_scope_matrix_gate


def _write_policy(repo: Path) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "runtime_api_scope_matrix_policy.json").write_text(
        json.dumps(
            {
                "required_scope_by_endpoint": {
                    "submit_job": "jobs:write",
                    "status": "jobs:read",
                },
                "forbid_additional_scope_validators": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_runtime_api_scope_matrix_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    (repo / "runtime" / "glyphser" / "api").mkdir(parents=True, exist_ok=True)
    (repo / "runtime" / "glyphser" / "api" / "runtime_api.py").write_text(
        """
class RuntimeApiService:
    def submit_job(self, payload, token, scope):
        _validate_scope(scope, expected=\"jobs:write\")
    def status(self, job_id, token, scope):
        _validate_scope(scope, expected=\"jobs:read\")
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_scope_matrix_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_scope_matrix_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_scope_matrix_gate.main([]) == 0


def test_runtime_api_scope_matrix_gate_fails_on_undocumented_scope(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    (repo / "runtime" / "glyphser" / "api").mkdir(parents=True, exist_ok=True)
    (repo / "runtime" / "glyphser" / "api" / "runtime_api.py").write_text(
        """
class RuntimeApiService:
    def submit_job(self, payload, token, scope):
        _validate_scope(scope, expected=\"jobs:write\")
    def status(self, job_id, token, scope):
        _validate_scope(scope, expected=\"jobs:read\")
    def replay(self, job_id, token, scope):
        _validate_scope(scope, expected=\"replay:run\")
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_scope_matrix_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_scope_matrix_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_scope_matrix_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "runtime_api_scope_matrix_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("undocumented_scope_validators:") for item in report["findings"])
