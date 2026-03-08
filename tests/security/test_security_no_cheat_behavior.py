from __future__ import annotations

import json
from pathlib import Path

from tooling.security import abuse_telemetry_snapshot, security_super_gate


def test_security_super_gate_does_not_swallow_subprocess_policy_errors(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)

    def _raise(*_args, **_kwargs):
        raise ValueError("subprocess policy denied")

    monkeypatch.setattr(security_super_gate, "run_checked", _raise)

    try:
        security_super_gate.main([])
    except ValueError as exc:
        assert "subprocess policy denied" in str(exc)
    else:
        raise AssertionError("expected fail-closed exception propagation")


def test_abuse_telemetry_snapshot_records_warn_instead_of_false_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "abuse_telemetry_policy.json").write_text(
        '{"runtime_api_state_path":"artifacts/generated/tmp/security/runtime_api_state.json"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_snapshot, "ROOT", repo)

    def _raise_import(_name: str):
        raise RuntimeError("simulated setup failure")

    monkeypatch.setattr(abuse_telemetry_snapshot.importlib, "import_module", _raise_import)
    assert abuse_telemetry_snapshot.main([]) == 0

    out = repo / "evidence" / "security" / "abuse_telemetry_snapshot.json"
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "WARN"
    assert any(str(item).startswith("snapshot_setup_failed:") for item in payload["findings"])
    assert payload["summary"]["correlation_ids"] == []


def test_abuse_telemetry_snapshot_includes_scan_toolchain_versions(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "tooling" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "abuse_telemetry_policy.json").write_text(
        '{"runtime_api_state_path":"artifacts/generated/tmp/security/runtime_api_state.json"}\n',
        encoding="utf-8",
    )
    (repo / "tooling" / "security" / "security_toolchain_lock.json").write_text(
        json.dumps(
            {
                "bandit": {"version": "1.9.4"},
                "pip-audit": {"version": "2.9.0"},
                "semgrep": {"version": "1.95.0"},
                "setuptools": {"version": "75.8.0"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_snapshot, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_snapshot, "SCAN_TOOLCHAIN_LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")

    def _raise_import(_name: str):
        raise RuntimeError("simulated setup failure")

    monkeypatch.setattr(abuse_telemetry_snapshot.importlib, "import_module", _raise_import)
    assert abuse_telemetry_snapshot.main([]) == 0
    payload = json.loads((repo / "evidence" / "security" / "abuse_telemetry_snapshot.json").read_text(encoding="utf-8"))
    assert payload["summary"]["toolchain_versions"]["bandit"] == "1.9.4"
    assert payload["summary"]["toolchain_versions"]["semgrep"] == "1.95.0"
