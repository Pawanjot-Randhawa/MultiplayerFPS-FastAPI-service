from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse, Response

from app.services.decompress import decode_godot_png

images = []

router = APIRouter(prefix="/image", tags=["image"])

@router.get("/connected")
def connected():
    return {"name": "Successfully connected to the anticheat server"}

@router.post("/upload")
def upload_image(image: bytes = Body(..., media_type="application/octet-stream")):
    decoded_image = decode_godot_png(image)
    images.append(decoded_image)
    return JSONResponse(
        content={
            "message": "Image uploaded and decoded successfully",
            "stored_content_type": "image/png",
            "stored_size": len(decoded_image),
        },
        status_code=200,
    )

@router.get("/latest")
def get_latest_image():
    if not images:
        raise HTTPException(status_code=404, detail="No images uploaded yet")

    image_bytes = images[-1]
    return Response(content=image_bytes, media_type="image/png")