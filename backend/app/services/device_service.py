from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviceModel
from app.schemas.devices import Device, DeviceCreate, DeviceUpdate


def _to_device(record: DeviceModel) -> Device:
    return Device(**record.__dict__)


def get_devices(db: Session) -> list[Device]:
    records = db.scalars(select(DeviceModel).order_by(DeviceModel.id))
    return [_to_device(record) for record in records]


def create_device(db: Session, payload: DeviceCreate) -> Device:
    now = datetime.now().isoformat()
    device = DeviceModel(
        id=f"dev-{uuid4().hex[:8]}",
        name=payload.name,
        category=payload.category,
        room=payload.room,
        status=payload.status,
        power_usage=payload.power_usage,
        health=payload.health,
        daily_active_hours=payload.daily_active_hours,
        last_seen=now,
        created_at=now,
        updated_at=now,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return _to_device(device)


def update_device(db: Session, device_id: str, payload: DeviceUpdate) -> Device:
    device = db.get(DeviceModel, device_id)
    if device:
        device.status = payload.status
        now = datetime.now().isoformat()
        device.last_seen = now
        device.updated_at = now
        db.commit()
        db.refresh(device)
        return _to_device(device)
    raise HTTPException(status_code=404, detail="Device not found")


def delete_device(db: Session, device_id: str) -> None:
    device = db.get(DeviceModel, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
