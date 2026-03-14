from __future__ import annotations


def safe_filename(name: str, *, suffix: str = ".json") -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        raise ValueError("name must be non-empty")
    if "/" in cleaned or "\\" in cleaned:
        raise ValueError("name must not contain path separators")
    if cleaned.startswith("."):
        raise ValueError("name must not start with '.'")
    if not cleaned.endswith(suffix):
        cleaned += suffix
    return cleaned

