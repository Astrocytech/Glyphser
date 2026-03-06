from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_script_reference_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_script_reference_gate_passes_with_referenced_new_script(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    workflows = repo / ".github" / "workflows"

    _write(sec / "existing_gate.py", "#!/usr/bin/env python3\n")
    _write(sec / "new_gate.py", "#!/usr/bin/env python3\n")
    _write(workflows / "ci.yml", "- run: python tooling/security/new_gate.py\n")
    _write(
        repo / "governance" / "security" / "security_script_reference_baseline.json",
        json.dumps({"known_scripts": ["tooling/security/existing_gate.py"]}, indent=2) + "\n",
    )
    _write(repo / "governance" / "security" / "security_script_reference_policy.json", '{"archived_scripts": []}\n')

    monkeypatch.setattr(security_script_reference_gate, "ROOT", repo)
    monkeypatch.setattr(security_script_reference_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(security_script_reference_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(
        security_script_reference_gate,
        "BASELINE",
        repo / "governance" / "security" / "security_script_reference_baseline.json",
    )
    monkeypatch.setattr(
        security_script_reference_gate,
        "POLICY",
        repo / "governance" / "security" / "security_script_reference_policy.json",
    )
    monkeypatch.setattr(security_script_reference_gate, "evidence_root", lambda: repo / "evidence")

    assert security_script_reference_gate.main([]) == 0


def test_security_script_reference_gate_fails_on_unreferenced_new_script(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    workflows = repo / ".github" / "workflows"

    _write(sec / "existing_gate.py", "#!/usr/bin/env python3\n")
    _write(sec / "new_gate.py", "#!/usr/bin/env python3\n")
    _write(workflows / "ci.yml", "name: ci\n")
    _write(
        repo / "governance" / "security" / "security_script_reference_baseline.json",
        json.dumps({"known_scripts": ["tooling/security/existing_gate.py"]}, indent=2) + "\n",
    )
    _write(repo / "governance" / "security" / "security_script_reference_policy.json", '{"archived_scripts": []}\n')

    monkeypatch.setattr(security_script_reference_gate, "ROOT", repo)
    monkeypatch.setattr(security_script_reference_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(security_script_reference_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(
        security_script_reference_gate,
        "BASELINE",
        repo / "governance" / "security" / "security_script_reference_baseline.json",
    )
    monkeypatch.setattr(
        security_script_reference_gate,
        "POLICY",
        repo / "governance" / "security" / "security_script_reference_policy.json",
    )
    monkeypatch.setattr(security_script_reference_gate, "evidence_root", lambda: repo / "evidence")

    assert security_script_reference_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_script_reference_gate.json").read_text(encoding="utf-8"))
    assert "unreferenced_new_security_script:tooling/security/new_gate.py" in report["findings"]


def test_security_script_reference_gate_passes_with_archived_new_script(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    workflows = repo / ".github" / "workflows"

    _write(sec / "existing_gate.py", "#!/usr/bin/env python3\n")
    _write(sec / "new_gate.py", "#!/usr/bin/env python3\n")
    _write(workflows / "ci.yml", "name: ci\n")
    _write(
        repo / "governance" / "security" / "security_script_reference_baseline.json",
        json.dumps({"known_scripts": ["tooling/security/existing_gate.py"]}, indent=2) + "\n",
    )
    _write(
        repo / "governance" / "security" / "security_script_reference_policy.json",
        json.dumps({"archived_scripts": ["tooling/security/new_gate.py"]}, indent=2) + "\n",
    )

    monkeypatch.setattr(security_script_reference_gate, "ROOT", repo)
    monkeypatch.setattr(security_script_reference_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(security_script_reference_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(
        security_script_reference_gate,
        "BASELINE",
        repo / "governance" / "security" / "security_script_reference_baseline.json",
    )
    monkeypatch.setattr(
        security_script_reference_gate,
        "POLICY",
        repo / "governance" / "security" / "security_script_reference_policy.json",
    )
    monkeypatch.setattr(security_script_reference_gate, "evidence_root", lambda: repo / "evidence")

    assert security_script_reference_gate.main([]) == 0


def test_security_script_reference_gate_fails_when_archived_script_still_wired(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    workflows = repo / ".github" / "workflows"

    _write(sec / "existing_gate.py", "#!/usr/bin/env python3\n")
    _write(workflows / "ci.yml", "- run: python tooling/security/existing_gate.py\n")
    _write(
        repo / "governance" / "security" / "security_script_reference_baseline.json",
        json.dumps({"known_scripts": ["tooling/security/existing_gate.py"]}, indent=2) + "\n",
    )
    _write(
        repo / "governance" / "security" / "security_script_reference_policy.json",
        json.dumps({"archived_scripts": ["tooling/security/existing_gate.py"]}, indent=2) + "\n",
    )

    monkeypatch.setattr(security_script_reference_gate, "ROOT", repo)
    monkeypatch.setattr(security_script_reference_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(security_script_reference_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(
        security_script_reference_gate,
        "BASELINE",
        repo / "governance" / "security" / "security_script_reference_baseline.json",
    )
    monkeypatch.setattr(
        security_script_reference_gate,
        "POLICY",
        repo / "governance" / "security" / "security_script_reference_policy.json",
    )
    monkeypatch.setattr(security_script_reference_gate, "evidence_root", lambda: repo / "evidence")

    assert security_script_reference_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_script_reference_gate.json").read_text(encoding="utf-8"))
    assert "archived_script_still_wired:tooling/security/existing_gate.py" in report["findings"]
