from fastapi import FastAPI

from app.api import image_router


app = FastAPI(
    title="FastAPI Anticheat",
    description="Temp anticheat application built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(image_router)

