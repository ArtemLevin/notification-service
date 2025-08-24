from datetime import datetime
from typing import Union

from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True
    message: Union[str, None] = None


class TimestampModel(BaseModel):
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
