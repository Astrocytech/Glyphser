import os
import tempfile
from pathlib import Path


def good_temp() -> str:
    fd, path = tempfile.mkstemp(prefix="glyphser-")
    os.close(fd)
    return path


def good_mode(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o750)
