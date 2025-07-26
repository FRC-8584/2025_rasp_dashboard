from modules import NetworkTable
from functools import lru_cache

from configs import NETWORK_TABLE_SERVER, NETWORK_TABLE_TABLE

@lru_cache()
def get_networktable() -> NetworkTable:
    return NetworkTable(NETWORK_TABLE_SERVER, NETWORK_TABLE_TABLE)