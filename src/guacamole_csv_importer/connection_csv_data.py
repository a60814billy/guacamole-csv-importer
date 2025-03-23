from dataclasses import dataclass
from typing import Dict


@dataclass
class ConnectionCsvData:
    __slots__ = [
        "site",
        "device_name",
        "hostname",
        "protocol",
        "port",
        "username",
        "password",
    ]

    site: str
    device_name: str
    hostname: str
    protocol: str
    port: str
    username: str
    password: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ConnectionCsvData":
        return cls(
            site=data["site"],
            device_name=data["device_name"],
            hostname=data["hostname"],
            protocol=data["protocol"],
            port=data["port"],
            username=data["username"],
            password=data["password"],
        )

    def to_dict(self):
        return {
            "site": self.site,
            "device_name": self.device_name,
            "hostname": self.hostname,
            "protocol": self.protocol,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }

    def to_create_dict(self):
        return {
            "name": self.device_name,
            "protocol": self.protocol,
            "parameters": {
                "hostname": self.hostname,
                "port": self.port,
                "username": self.username,
                "password": self.password,
            },
        }
