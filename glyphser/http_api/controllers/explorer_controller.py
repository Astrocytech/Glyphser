from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.glyphser.security.path_guard import resolve_inside_root, validate_path_text


@dataclass(frozen=True)
class ExplorerEntry:
    name: str
    kind: str


class ExplorerController:
    def __init__(self, *, repo_root: Path, work_root: Path) -> None:
        self._repo_root = repo_root.resolve()
        self._work_root = work_root.resolve()

    def roots(self) -> dict[str, str]:
        return {
            "repo": str(self._repo_root),
            "docs": str(self._repo_root / "docs"),
            "specs": str(self._repo_root / "specs"),
            "artifacts": str(self._repo_root / "artifacts"),
            "evidence": str(self._repo_root / "evidence"),
            "runtime": str(self._repo_root / "runtime"),
            "glyphser": str(self._repo_root / "glyphser"),
            "workspace": str(self._work_root),
        }

    def list_dir(self, *, root_label: str, rel_path: str) -> list[dict[str, Any]]:
        root = self._root_path(root_label)
        clean = validate_path_text(rel_path or ".", field_name="path")
        target = resolve_inside_root(root / clean, root=root, require_exists=True)
        if not target.exists() or not target.is_dir():
            raise ValueError("path is not a directory")

        out: list[dict[str, Any]] = []
        for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            if child.is_symlink():
                continue
            kind = "dir" if child.is_dir() else "file"
            out.append({"name": child.name, "kind": kind})
        return out

    def read_text(self, *, root_label: str, rel_path: str, max_bytes: int = 1_000_000) -> str:
        root = self._root_path(root_label)
        clean = validate_path_text(rel_path, field_name="path")
        target = resolve_inside_root(root / clean, root=root, require_exists=True)
        if not target.exists() or not target.is_file():
            raise ValueError("path is not a file")
        data = target.read_bytes()
        if len(data) > max_bytes:
            raise ValueError("file too large")
        return data.decode("utf-8", errors="replace")

    def _root_path(self, label: str) -> Path:
        label = (label or "").strip().lower()
        roots = self.roots()
        if label not in roots:
            raise ValueError("unknown root")
        return Path(roots[label]).resolve()
