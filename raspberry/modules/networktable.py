from networktables import NetworkTables
import time

class NetworkTable:
    def __init__(self, server: str, table_name: str):
        NetworkTables.initialize(server=server)
        self.table = NetworkTables.getTable(table_name)
        self.listeners = []

    def put_number(self, key: str, value: float):
        self.table.putNumber(key, value)

    def get_number(self, key: str, default: float = 0.0) -> float:
        return self.table.getNumber(key, default)

    def put_string(self, key: str, value: str):
        self.table.putString(key, value)

    def get_string(self, key: str, default: str = "") -> str:
        return self.table.getString(key, default)
    
    def put_boolean(self, key: str, value: bool):
        self.table.putBoolean(key, value)

    def get_booloen(self, key: str, default: bool = False) -> bool:
        return self.table.getBoolean(key, default)

    def add_listener(self, callback):
        self.table.addEntryListener(callback)
        self.listeners.append(callback)

    @property
    def is_connected(self) -> bool:
        return NetworkTables.isConnected()