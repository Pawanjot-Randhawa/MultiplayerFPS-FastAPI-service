import base64
import zlib

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response

images = []

app = FastAPI(
    title="FastAPI Anticheat",
    description="Temp anticheat application built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/connected")
def connected():
    return {"name": "Successfully connected to the anticheat server"}


def detect_image_content_type(image_bytes: bytes) -> str:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if image_bytes.startswith(b"BM"):
        return "image/bmp"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


def build_data_url(image_bytes: bytes, content_type: str) -> str:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{image_base64}"


def decode_godot_deflate_png(payload: bytes) -> bytes:
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


@app.post("/upload")
def upload_image(image: bytes = Body(..., media_type="application/octet-stream")):
    decoded_image = decode_godot_deflate_png(image)
    images.append(decoded_image)
    return JSONResponse(
        content={
            "message": "Image uploaded and decoded successfully",
            "stored_content_type": detect_image_content_type(decoded_image),
            "stored_size": len(decoded_image),
        },
        status_code=200,
    )


@app.get("/image/latest")
def get_latest_image():
    if not images:
        raise HTTPException(status_code=404, detail="No images uploaded yet")

    image_bytes = images[-1]
    content_type = detect_image_content_type(image_bytes)
    return Response(content=image_bytes, media_type=content_type)


@app.get("/image/latest/base64")
def get_latest_image_base64():
    if not images:
        raise HTTPException(status_code=404, detail="No images uploaded yet")

    image_bytes = images[-1]
    content_type = detect_image_content_type(image_bytes)
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    return {
        "content_type": content_type,
        "base64": image_base64,
        "data_url": build_data_url(image_bytes, content_type),
    }