from modules import Camera
from functools import lru_cache

from configs import CAMERA_RETRY_INTERVAL

@lru_cache()
def get_camera() -> Camera:
    return Camera(0, CAMERA_RETRY_INTERVAL)