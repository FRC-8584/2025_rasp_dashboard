from pydantic import BaseModel
from typing import Optional

class FrameMessage(BaseModel):
    error: bool
    message: str
    image: Optional[str]
    time_stamp: float