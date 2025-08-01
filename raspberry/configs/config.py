import json
from pathlib import Path
from typing import List
from pydantic import BaseModel

class NetworkTableConfigsModel(BaseModel):
    server: str
    table: str

class FrontendConfigsModel(BaseModel):
    url: str
class ConfigsModel(BaseModel):
    host: str
    port: int
    camera_retry_interval: int
    allowed_origins: List[str]
    network_table: NetworkTableConfigsModel
    frontend: FrontendConfigsModel

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
            camera_retry_interval=3,
            network_table=NetworkTableConfigsModel(
                server = "10.XX.XX.2",
                table = "raspberry_pi"
            )
        )
        f.write(configs.model_dump_json(indent=4))

    print("`configs.json` not found, please refill it.")
    print(configs.model_dump_json(indent=4))

HOST = configs.host
PORT = configs.port
ALLOWED_ORIGINS = configs.allowed_origins
CAMERA_RETRY_INTERVAL = configs.camera_retry_interval

NETWORK_TABLE_SERVER = configs.network_table.server
NETWORK_TABLE_TABLE = configs.network_table.table

