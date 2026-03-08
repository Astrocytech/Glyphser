from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import runbook_command_health_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


class _Proc:
    def __init__(self, returncode: int, *, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_runbook_command_health_gate_passes_when_commands_succeed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "runbook_command_health_checks.json"
    _write_json(policy, {"commands": [{"cmd": ["python", "--version"]}]})
    _sign(policy)

    monkeypatch.setattr(runbook_command_health_gate, "ROOT", repo)
    monkeypatch.setattr(runbook_command_health_gate, "POLICY", policy)
    monkeypatch.setattr(runbook_command_health_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(runbook_command_health_gate, "run_checked", lambda *a, **k: _Proc(0))
    assert runbook_command_health_gate.main([]) == 0


def test_runbook_command_health_gate_fails_when_command_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "runbook_command_health_checks.json"
    _write_json(policy, {"commands": [{"cmd": ["python", "--version"]}]})
    _sign(policy)

    monkeypatch.setattr(runbook_command_health_gate, "ROOT", repo)
    monkeypatch.setattr(runbook_command_health_gate, "POLICY", policy)
    monkeypatch.setattr(runbook_command_health_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(runbook_command_health_gate, "run_checked", lambda *a, **k: _Proc(1))
    assert runbook_command_health_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "runbook_command_health_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("runbook_command_failed:") for item in report["findings"])


def test_runbook_command_health_gate_fails_on_runbook_cli_option_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "runbook_command_health_checks.json"
    _write_json(policy, {"commands": []})
    _sign(policy)
    (repo / "governance" / "security" / "LOCAL.md").write_text(
        "Run `python tooling/security/demo_gate.py --unknown-flag`.\n",
        encoding="utf-8",
    )

    def _runner(cmd: list[str], **_: object) -> _Proc:
        if len(cmd) >= 3 and cmd[1] == "tooling/security/demo_gate.py" and cmd[2] == "--help":
            return _Proc(0, stdout="usage: demo_gate.py [--known-flag]\n")
        return _Proc(0)

    monkeypatch.setattr(runbook_command_health_gate, "ROOT", repo)
    monkeypatch.setattr(runbook_command_health_gate, "POLICY", policy)
    monkeypatch.setattr(runbook_command_health_gate, "RUNBOOK_DOC_ROOTS", (repo / "governance" / "security",))
    monkeypatch.setattr(runbook_command_health_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(runbook_command_health_gate, "run_checked", _runner)
    assert runbook_command_health_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "runbook_command_health_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("runbook_option_not_supported:") for item in report["findings"])
