from __future__ import annotations

import json
from pathlib import Path

from tooling.security import docs_snippet_pinning_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_docs_snippet_pinning_gate_passes_when_action_refs_are_immutable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "docs_snippet_pinning_policy.json"
    _write_json(policy, {"scan_globs": ["docs/ci/*.yml"], "enforce_action_sha_pinning": True})
    (repo / "docs" / "ci").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "ci" / "sample.yml").write_text(
        "jobs:\n  x:\n    steps:\n      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(docs_snippet_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(docs_snippet_pinning_gate, "POLICY", policy)
    monkeypatch.setattr(docs_snippet_pinning_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_snippet_pinning_gate.main([]) == 0


def test_docs_snippet_pinning_gate_fails_when_action_refs_are_tags(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "docs_snippet_pinning_policy.json"
    _write_json(policy, {"scan_globs": ["docs/ci/*.yml"], "enforce_action_sha_pinning": True})
    (repo / "docs" / "ci").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "ci" / "sample.yml").write_text(
        "jobs:\n  x:\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(docs_snippet_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(docs_snippet_pinning_gate, "POLICY", policy)
    monkeypatch.setattr(docs_snippet_pinning_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_snippet_pinning_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "docs_snippet_pinning_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("unpinned_action_ref:") for item in report["findings"])
