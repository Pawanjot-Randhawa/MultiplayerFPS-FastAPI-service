from pydantic import BaseModel

class StatsResponse(BaseModel):
    uploads: int
    gemini_triggers: int
    saved_calls: int
    trigger_rate_percent: float
    reduced_percent: float

class UploadResponse(BaseModel):
    message: str
    flag: str

class ConnectionResponse(BaseModel):
    message: str
    