from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
import json
import time
from pathlib import Path

from tooling.security import security_super_gate


class _Proc:
    def __init__(self, rc: int) -> None:
        self.returncode = rc
        self.stdout = ""
        self.stderr = ""


def test_security_super_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    assert security_super_gate.main([]) == 0
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "PASS"
    assert out["metadata"]["subprocess_timeout_sec"] == security_super_gate.SUPER_GATE_SUBPROCESS_TIMEOUT_SEC
    assert out["metadata"]["subprocess_max_output_bytes"] == security_super_gate.SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES
    assert all("runtime_seconds" in item for item in out.get("results", []))


def test_security_super_gate_fails_on_subgate_failure(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)

    calls = {"n": 0}

    def _run(*a, **k):
        calls["n"] += 1
        return _Proc(1 if calls["n"] == 2 else 0)

    monkeypatch.setattr(security_super_gate, "run_checked", _run)
    assert security_super_gate.main([]) == 1


def test_security_super_gate_reports_prereq_diagnostics(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: None)
    monkeypatch.delenv("TZ", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)
    assert security_super_gate.main(["--strict-prereqs", "--strict-key"]) == 1
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    diagnostics = out["metadata"]["prereq_diagnostics"]
    assert diagnostics
    assert all("finding" in d and "remediation" in d for d in diagnostics)


def test_security_super_gate_core_passes_minimal_strict_ci_profile(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: "/usr/bin/tool")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "test-key")

    assert security_super_gate.main(["--strict-prereqs", "--strict-key"]) == 0
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "PASS"
    assert out["summary"]["prereq_failures"] == 0


def test_security_super_gate_strict_key_missing_secret_reports_clear_failure(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: "/usr/bin/tool")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)

    assert security_super_gate.main(["--strict-prereqs", "--strict-key"]) == 1
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert "missing_env:GLYPHSER_PROVENANCE_HMAC_KEY" in out["findings"]
    diagnostics = out.get("metadata", {}).get("prereq_diagnostics", [])
    assert any(
        isinstance(item, dict)
        and item.get("finding") == "missing_env:GLYPHSER_PROVENANCE_HMAC_KEY"
        and "GLYPHSER_PROVENANCE_HMAC_KEY" in str(item.get("remediation", ""))
        for item in diagnostics
    )


def test_security_super_gate_supports_partial_rerun_and_deterministic_aggregation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))

    args = ["--only-gate", "tooling/security/security_toolchain_gate.py", "--only-gate", "tooling/security/semgrep_rules_self_check_gate.py"]
    assert security_super_gate.main(args) == 0
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    scripts = [str(item.get("cmd", ["", ""])[1]) for item in out.get("results", []) if isinstance(item, dict)]
    assert scripts == ["tooling/security/security_toolchain_gate.py", "tooling/security/semgrep_rules_self_check_gate.py"]
    digest_a = out["summary"]["aggregation_digest"]

    args_reordered = [
        "--only-gate",
        "tooling/security/semgrep_rules_self_check_gate.py",
        "--only-gate",
        "tooling/security/security_toolchain_gate.py",
    ]
    assert security_super_gate.main(args_reordered) == 0
    out2 = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    digest_b = out2["summary"]["aggregation_digest"]
    assert digest_a == digest_b


def test_security_super_gate_model_based_failure_propagation_for_selected_gates(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: "/usr/bin/tool")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "test-key")

    selected = [
        "tooling/security/security_toolchain_gate.py",
        "tooling/security/workflow_artifact_retention_gate.py",
        "tooling/security/promotion_policy_gate.py",
    ]

    for state in product((0, 1), repeat=len(selected)):
        rc_map = dict(zip(selected, state))

        def _run_checked(cmd, **kwargs):  # type: ignore[no-untyped-def]
            _ = kwargs
            return _Proc(rc_map.get(str(cmd[1]), 0))

        monkeypatch.setattr(security_super_gate, "run_checked", _run_checked)
        args: list[str] = []
        for gate in selected:
            args.extend(["--only-gate", gate])
        assert security_super_gate.main(args) == (0 if all(x == 0 for x in state) else 1)

        out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
        expected_failed = sum(1 for rc in state if rc != 0)
        expected_passed = len(state) - expected_failed
        expected_findings = {
            "gate_failed:" + " ".join([security_super_gate.sys.executable, gate]) for gate, rc in rc_map.items() if rc != 0
        }

        assert out["summary"]["total"] == len(state)
        assert out["summary"]["failed"] == expected_failed
        assert out["summary"]["passed"] == expected_passed
        assert out["status"] == ("PASS" if expected_failed == 0 else "FAIL")
        assert set(out["findings"]) == expected_findings


def test_security_super_gate_model_based_prereq_failure_propagation(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: None)
    monkeypatch.delenv("TZ", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))

    gate = "tooling/security/security_toolchain_gate.py"
    assert security_super_gate.main(["--strict-prereqs", "--strict-key", "--only-gate", gate]) == 1
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    prereq_findings = {
        "missing_tool:semgrep",
        "missing_tool:pip-audit",
        "missing_env:TZ",
        "missing_env:LC_ALL",
        "missing_env:LANG",
        "missing_env:GLYPHSER_PROVENANCE_HMAC_KEY",
    }
    assert out["summary"]["failed"] == 0
    assert out["summary"]["prereq_failures"] == len(prereq_findings)
    assert out["status"] == "FAIL"
    assert prereq_findings.issubset(set(out["findings"]))


def test_security_super_gate_concurrent_execution_simulation_has_deterministic_aggregation(monkeypatch) -> None:
    cmds = [
        [security_super_gate.sys.executable, "tooling/security/a_gate.py"],
        [security_super_gate.sys.executable, "tooling/security/b_gate.py"],
        [security_super_gate.sys.executable, "tooling/security/c_gate.py"],
    ]

    def _run_checked(cmd, **kwargs):  # type: ignore[no-untyped-def]
        _ = kwargs
        script = str(cmd[1])
        if script.endswith("a_gate.py"):
            time.sleep(0.03)
            return _Proc(0)
        if script.endswith("b_gate.py"):
            time.sleep(0.01)
            return _Proc(1)
        time.sleep(0.02)
        return _Proc(0)

    monkeypatch.setattr(security_super_gate, "run_checked", _run_checked)

    def _collect_results() -> list[dict]:
        out: list[dict] = []
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(security_super_gate._run, cmd) for cmd in cmds]
            for fut in as_completed(futures):
                out.append(fut.result())
        return out

    run_a = _collect_results()
    run_b = _collect_results()
    digest_a = security_super_gate._aggregation_digest(run_a)
    digest_b = security_super_gate._aggregation_digest(run_b)
    assert digest_a == digest_b


def test_security_super_gate_repeated_invocation_is_idempotent_for_all_manifest_gates(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))

    assert security_super_gate.main(["--include-extended"]) == 0
    first = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert security_super_gate.main(["--include-extended"]) == 0
    second = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))

    assert first["summary"]["total"] == second["summary"]["total"]
    assert first["summary"]["total"] > 0
    assert first["summary"]["aggregation_digest"] == second["summary"]["aggregation_digest"]
    scripts_first = [str(item.get("cmd", ["", ""])[1]) for item in first.get("results", []) if isinstance(item, dict)]
    scripts_second = [str(item.get("cmd", ["", ""])[1]) for item in second.get("results", []) if isinstance(item, dict)]
    assert scripts_first == scripts_second


def test_security_super_gate_explainability_mode_emits_rule_ids_and_why(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)

    calls = {"n": 0}

    def _run(*a, **k):
        _ = (a, k)
        calls["n"] += 1
        return _Proc(1 if calls["n"] == 1 else 0)

    monkeypatch.setattr(security_super_gate, "run_checked", _run)
    assert security_super_gate.main(["--only-gate", "tooling/security/security_toolchain_gate.py", "--explainability"]) == 1
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    explainability = out.get("explainability", {})
    assert explainability.get("schema_version") == "glyphser-security-super-gate-explainability.v1"
    decisions = explainability.get("critical_decisions", [])
    assert isinstance(decisions, list) and decisions
    assert any(
        isinstance(item, dict)
        and item.get("decision_id") == "security_super_gate_overall"
        and item.get("decision") == "FAIL"
        and item.get("rule_id") == security_super_gate.RULE_ID_SUPER_GATE_FAIL
        and "why" in item
        for item in decisions
    )
    assert any(
        isinstance(item, dict)
        and str(item.get("decision_id", "")).startswith("subgate:")
        and item.get("decision") == "FAIL"
        and item.get("rule_id") == security_super_gate.RULE_ID_SUBGATE_FAIL
        and "why" in item
        for item in decisions
    )


def test_security_super_gate_explainability_mode_maps_prereq_rule_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    monkeypatch.setattr(security_super_gate.shutil, "which", lambda _: None)
    monkeypatch.delenv("TZ", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)

    assert security_super_gate.main(["--strict-prereqs", "--strict-key", "--explainability"]) == 1
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    decisions = out.get("explainability", {}).get("critical_decisions", [])
    prereq_decisions = [
        item for item in decisions if isinstance(item, dict) and str(item.get("decision_id", "")).startswith("prereq:")
    ]
    assert prereq_decisions
    rule_ids = {str(item.get("rule_id", "")) for item in prereq_decisions}
    assert security_super_gate.RULE_ID_PREREQ_MISSING_TOOL in rule_ids
    assert security_super_gate.RULE_ID_PREREQ_MISSING_ENV in rule_ids


def test_security_super_gate_explainability_emits_deterministic_rule_trace(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))

    args = ["--only-gate", "tooling/security/security_toolchain_gate.py", "--explainability"]
    assert security_super_gate.main(args) == 0
    first = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert security_super_gate.main(args) == 0
    second = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))

    trace_a = first.get("explainability", {}).get("rule_evaluation_trace", [])
    trace_b = second.get("explainability", {}).get("rule_evaluation_trace", [])
    assert trace_a == trace_b
    assert isinstance(trace_a, list) and trace_a
    assert trace_a[0]["subject"] == "security_super_gate_overall"
    assert trace_a[0]["rule_id"] == security_super_gate.RULE_ID_SUPER_GATE_PASS
    assert trace_a[0]["decision"] == "PASS"
    assert [entry["step"] for entry in trace_a] == list(range(1, len(trace_a) + 1))
