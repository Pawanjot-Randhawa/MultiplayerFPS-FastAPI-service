"""Utilities for decoding Godot-compressed PNG payloads.

This module accepts either:
- raw PNG bytes, or
- DEFLATE-compressed payloads that expand to a PNG.
"""

import zlib

from fastapi import HTTPException


def decode_godot_png(payload: bytes) -> bytes:
    """Decode a payload into PNG bytes.

    The function first checks whether the input is already a PNG by inspecting
    the PNG file signature. If not, it attempts zlib decompression using both
    wrapped DEFLATE and raw DEFLATE modes (Godot can emit either format).

    Args:
        payload: Incoming binary payload from the client.

    Returns:
        Valid PNG bytes.

    Raises:
        HTTPException: If the payload is neither a PNG nor a DEFLATE stream
            that decompresses to a PNG.
    """
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return payload

    try:
        decompressed = zlib.decompress(payload)
        if decompressed.startswith(b"\x89PNG\r\n\x1a\n"):
            return decompressed
    except zlib.error:
        pass

    try:
        decompressed = zlib.decompress(payload, -zlib.MAX_WBITS)
        if decompressed.startswith(b"\x89PNG\r\n\x1a\n"):
            return decompressed
    except zlib.error:
        pass

    raise HTTPException(
        status_code=400,
        detail="Upload is not a PNG or Godot DEFLATE-compressed PNG payload",
    )