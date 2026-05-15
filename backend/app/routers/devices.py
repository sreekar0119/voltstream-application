from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.devices import Device, DeviceCreate, DeviceUpdate
from app.services.device_service import create_device, delete_device, get_devices, update_device

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[Device])
def all_devices(db: Session = Depends(get_db)) -> list[Device]:
    return get_devices(db)


@router.post("", response_model=Device, status_code=status.HTTP_201_CREATED)
def add_device(payload: DeviceCreate, db: Session = Depends(get_db)) -> Device:
    return create_device(db, payload)


@router.patch("/{device_id}", response_model=Device)
def patch_device(device_id: str, payload: DeviceUpdate, db: Session = Depends(get_db)) -> Device:
    return update_device(db, device_id, payload)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_device(device_id: str, db: Session = Depends(get_db)) -> Response:
    delete_device(db, device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
