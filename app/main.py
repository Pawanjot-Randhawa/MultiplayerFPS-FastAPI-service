from fastapi import FastAPI
from fastapi.responses import JSONResponse

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