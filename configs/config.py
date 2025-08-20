import json
from pathlib import Path
from typing import List
from pydantic import BaseModel

class ProfileConfigs(BaseModel):
    width: int
    height: int
    fps: int

class GeminiConfigs(BaseModel):
    color_profile: ProfileConfigs
    depth_profile: ProfileConfigs

class ConfigsModel(BaseModel):
    host: str
    port: int
    allowed_origins: List[str]

    gemini_configs: GeminiConfigs

CONFIG_PATH = Path(__file__).parent.parent / "configs.json"

try:
    with open(CONFIG_PATH, mode="r") as f:
        _json = json.loads(f.read().encode("utf-8"))
        configs = ConfigsModel(**_json)

except Exception as e:
    with open(CONFIG_PATH, mode="w") as f:
        configs = ConfigsModel(
            host="0.0.0.0",
            port=8000,
            allowed_origins=["*"],
            gemini_configs= GeminiConfigs(
                color_profile=ProfileConfigs(
                    width=640,
                    height=480,
                    fps=30
                ),
                depth_profile=ProfileConfigs(
                    width=640,
                    height=400,
                    fps=30
                ),
            )
        )
        f.write(configs.model_dump_json(indent=4))

    print("`configs.json` not found, please refill it.")
    print(configs.model_dump_json(indent=4))
    exit()

HOST = configs.host
PORT = configs.port
ALLOWED_ORIGINS = configs.allowed_origins

COLOR_PROFILE_WIDTH = configs.gemini_configs.color_profile.width
COLOR_PROFILE_HEIGHT = configs.gemini_configs.color_profile.height
COLOR_PROFILE_FPS = configs.gemini_configs.color_profile.fps

DEPTH_PROFILE_WIDTH = configs.gemini_configs.depth_profile.width
DEPTH_PROFILE_HEIGHT = configs.gemini_configs.depth_profile.height
DEPTH_PROFILE_FPS = configs.gemini_configs.depth_profile.fps
