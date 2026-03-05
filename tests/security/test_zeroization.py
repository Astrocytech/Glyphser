from __future__ import annotations

from runtime.glyphser.security.zeroization import secret_bytes_buffer, zeroize_bytearray


def test_zeroize_bytearray_overwrites_all_bytes() -> None:
    buf = bytearray(b"super-secret")
    zeroize_bytearray(buf)
    assert buf == bytearray(len(buf))


def test_secret_bytes_buffer_zeroizes_on_exit() -> None:
    captured = bytearray()
    with secret_bytes_buffer("runtime-api-secret") as buf:
        captured = buf
        assert bytes(buf) == b"runtime-api-secret"
    assert captured == bytearray(len(captured))
