from pydantic import BaseModel
from datetime import datetime

class BaseResponse(BaseModel):
    success: bool = True
    message: str | None = None

class TimestampModel(BaseModel):
    created_at: datetime = None
    updated_at: datetime | None = None