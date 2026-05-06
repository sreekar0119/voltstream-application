from datetime import datetime

from fastapi import HTTPException

from app.schemas.devices import Device, DeviceUpdate
from app.utils.data_loader import read_json, write_json


def get_devices() -> list[Device]:
    return [Device(**record) for record in read_json("devices.json")]


def update_device(device_id: str, payload: DeviceUpdate) -> Device:
    devices = read_json("devices.json")
    for device in devices:
        if device["id"] == device_id:
            device["status"] = payload.status
            device["last_seen"] = datetime.now().isoformat()
            write_json("devices.json", devices)
            return Device(**device)
    raise HTTPException(status_code=404, detail="Device not found")
