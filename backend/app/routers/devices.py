from fastapi import APIRouter

from app.schemas.devices import Device, DeviceUpdate
from app.services.device_service import get_devices, update_device

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[Device])
def all_devices() -> list[Device]:
    return get_devices()


@router.patch("/{device_id}", response_model=Device)
def patch_device(device_id: str, payload: DeviceUpdate) -> Device:
    return update_device(device_id, payload)
