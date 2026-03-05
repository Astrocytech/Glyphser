from __future__ import annotations

import json
from pathlib import Path

from tooling.security import required_control_condition_bypass_gate, unconditional_return_zero_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _workflow_from_controls(controls: list[str], *, mutate_first_control: bool) -> str:
    lines = ["jobs:", "  security:", "    steps:"]
    for idx, control in enumerate(controls):
        lines.append(f"      - name: Control {idx}")
        if mutate_first_control and idx == 0:
            lines.append("        if: always()")
        lines.append(f"        run: {control}")
    return "\n".join(lines) + "\n"


def test_mutation_anti_bypass_flags_unconditional_return_zero_in_orchestrator(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    ev = repo / "evidence" / "security"
    _write(sec / "security_super_gate.py", "def main(argv=None):\n    return 0\n")

    monkeypatch.setattr(unconditional_return_zero_gate, "ROOT", repo)
    monkeypatch.setattr(unconditional_return_zero_gate, "evidence_root", lambda: repo / "evidence")
    assert unconditional_return_zero_gate.main([]) == 1
    report = json.loads((ev / "unconditional_return_zero_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("unconditional_return_zero:security_super_gate.py:") for item in report["findings"])


def test_mutation_anti_bypass_flags_conditional_workflow_guard_bypass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf_root = repo / ".github" / "workflows"
    controls = required_control_condition_bypass_gate.WORKFLOW_CONTROLS[".github/workflows/ci.yml"]
    _write(wf_root / "ci.yml", _workflow_from_controls(controls, mutate_first_control=False))
    _write(wf_root / "release.yml", _workflow_from_controls(controls, mutate_first_control=False))
    _write(wf_root / "security-maintenance.yml", _workflow_from_controls(controls, mutate_first_control=True))

    monkeypatch.setattr(required_control_condition_bypass_gate, "ROOT", repo)
    monkeypatch.setattr(required_control_condition_bypass_gate, "evidence_root", lambda: repo / "evidence")
    assert required_control_condition_bypass_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "required_control_condition_bypass_gate.json").read_text("utf-8"))
    assert any(str(item).startswith("conditional_critical_control:") for item in report["findings"])
