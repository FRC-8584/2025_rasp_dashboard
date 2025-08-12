from pydantic import BaseModel
from typing import Optional

class CameraStatus(BaseModel):
    error: bool
    connected: bool
    t_x: float
    t_y: float
    t_a: float
    depth: float
    color_image_base64: Optional[str]
    depth_image_base64: Optional[str]
    message: str