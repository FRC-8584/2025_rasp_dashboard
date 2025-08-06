import json
from pathlib import Path
from typing import List
from pydantic import BaseModel

class ConfigsModel(BaseModel):
    host: str
    port: int
    allowed_origins: List[str]
    proxy_server_url: str

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
            proxy_server_url="http://127.0.0.1:9487"
        )
        f.write(configs.model_dump_json(indent=4))

    print("`configs.json` not found, please refill it.")
    print(configs.model_dump_json(indent=4))
    exit()

HOST = configs.host
PORT = configs.port
ALLOWED_ORIGINS = configs.allowed_origins
PROXY_SERVER_URL = configs.proxy_server_url
