"""Utilities for best-effort in-memory secret zeroization."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


def zeroize_bytearray(buf: bytearray) -> None:
    """Overwrite a mutable byte buffer in place.

    Python cannot guarantee full memory cleansing for all objects, but this
    reduces exposure for sensitive values held in mutable buffers.
    """

    for ix in range(len(buf)):
        buf[ix] = 0


@contextmanager
def secret_bytes_buffer(secret: str | bytes, *, encoding: str = "utf-8") -> Iterator[bytearray]:
    """Yield mutable secret bytes and always zeroize them on exit.

    This does not zeroize the original immutable Python object; it provides a
    practical strategy for handling temporary copies used in cryptographic or
    protocol operations.
    """

    if isinstance(secret, bytes):
        buf = bytearray(secret)
    else:
        buf = bytearray(secret.encode(encoding))
    try:
        yield buf
    finally:
        zeroize_bytearray(buf)
