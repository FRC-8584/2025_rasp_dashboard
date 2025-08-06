from modules import Camera
from functools import lru_cache

@lru_cache()
def get_camera() -> Camera:
    return Camera(0, 3)