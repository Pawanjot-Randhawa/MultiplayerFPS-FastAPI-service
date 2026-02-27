from threading import Lock

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.responses import StatsResponse, UploadResponse, ConnectionResponse
from app.services.decompress import decode_godot_png
from app.services.filter import filter_image_bytes
from app.services.gemini_filter import filter_image_bytes_gemini

stats_lock = Lock()
total_uploads = 0
gemini_triggers = 0

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/upload", response_model=UploadResponse)
def upload_image(image: bytes = Body(..., media_type="application/octet-stream")):
    global total_uploads, gemini_triggers

    decoded_image = decode_godot_png(image)

    msg = "Filtered"

    with stats_lock:
        total_uploads += 1

    flag = filter_image_bytes(decoded_image)

    if flag == "suspected":
        with stats_lock:
            gemini_triggers += 1
        flag = filter_image_bytes_gemini(decoded_image)
        msg = "Gemini Filter"
    
    return UploadResponse(
        message=msg,
        flag=flag,
    )

@router.get("/stats", response_model=StatsResponse)
def get_image_stats():
    with stats_lock:
        total = total_uploads
        gemini = gemini_triggers

    saved_calls = total - gemini
    trigger_rate = (gemini / total * 100) if total else 0.0
    reduced_percent = (saved_calls / total * 100) if total else 0.0

    return StatsResponse(
        uploads=total,
        gemini_triggers=gemini,
        saved_calls=saved_calls,
        trigger_rate_percent=round(trigger_rate, 2),
        reduced_percent=round(reduced_percent, 2),
    )

@router.get("/connection", response_model=ConnectionResponse)
def check_connection():
    return ConnectionResponse(message="Connected")