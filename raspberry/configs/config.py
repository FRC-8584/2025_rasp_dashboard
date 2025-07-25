import json
from pathlib import Path
from typing import List
from pydantic import BaseModel

class NetworkTableConfigsModel(BaseModel):
    server: str
    table: str

class FrontendConfigsModel(BaseModel):
    url: str
    allowed_origins: List[str]

class ConfigsModel(BaseModel):
    host: str
    port: int
    camera_retry_interval: int
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
            host="localhost",
            port=8000,
            camera_retry_interval=5,
            network_table=NetworkTableConfigsModel(
                server = "10.XX.XX.2",
                table = "raspberry_pi"
            ),
            frontend=FrontendConfigsModel(
                url="http://127.0.0.1:3000",
                allowed_origins=["http://127.0.0.1:3000"]
            )
        )
        f.write(configs.model_dump_json(indent=4))

    print("`configs.json` not found, please refill it.")
    print(configs.model_dump_json(indent=4))

HOST = configs.host
PORT = configs.port
DEBUG = configs.debug