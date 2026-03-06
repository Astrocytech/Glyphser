from __future__ import annotations

import json
from pathlib import Path

from tooling.security import sarif_fallback_upload_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_sarif_fallback_upload_gate_passes_with_push_only_code_scanning_and_unconditional_fallback(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Upload SARIF to Code Scanning",
                "        if: github.event_name == 'push'",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: semgrep.sarif",
                "      - name: Upload security artifacts",
                "        uses: actions/upload-artifact@x",
                "        with:",
                "          path: semgrep.json",
            ]
        )
        + "\n",
    )

    monkeypatch.setattr(sarif_fallback_upload_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_fallback_upload_gate, "CI_WORKFLOW", repo / ".github" / "workflows" / "ci.yml")
    monkeypatch.setattr(sarif_fallback_upload_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_fallback_upload_gate.main([]) == 0


def test_sarif_fallback_upload_gate_fails_when_code_scanning_upload_is_unguarded(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Upload SARIF to Code Scanning",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: semgrep.sarif",
                "      - name: Upload security artifacts",
                "        uses: actions/upload-artifact@x",
                "        with:",
                "          path: semgrep.json",
            ]
        )
        + "\n",
    )

    monkeypatch.setattr(sarif_fallback_upload_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_fallback_upload_gate, "CI_WORKFLOW", repo / ".github" / "workflows" / "ci.yml")
    monkeypatch.setattr(sarif_fallback_upload_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_fallback_upload_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "sarif_fallback_upload_gate.json").read_text(encoding="utf-8"))
    assert "missing_code_scanning_skip_guard:Upload SARIF to Code Scanning" in report["findings"]


def test_sarif_fallback_upload_gate_fails_when_fallback_upload_is_push_only(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Upload SARIF to Code Scanning",
                "        if: github.event_name == 'push'",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: semgrep.sarif",
                "      - name: Upload security artifacts",
                "        if: github.event_name == 'push'",
                "        uses: actions/upload-artifact@x",
                "        with:",
                "          path: semgrep.json",
            ]
        )
        + "\n",
    )

    monkeypatch.setattr(sarif_fallback_upload_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_fallback_upload_gate, "CI_WORKFLOW", repo / ".github" / "workflows" / "ci.yml")
    monkeypatch.setattr(sarif_fallback_upload_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_fallback_upload_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "sarif_fallback_upload_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("fallback_upload_not_available_on_pull_request:") for item in report["findings"])
