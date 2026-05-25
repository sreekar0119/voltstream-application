from __future__ import annotations

import re
from datetime import datetime
from difflib import SequenceMatcher
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviceModel


def _device_payload(device: DeviceModel) -> dict:
    return {
        "id": device.id,
        "name": device.name,
        "category": device.category,
        "room": getattr(device, "room", "General") or "General",
        "status": device.status,
        "power_usage": device.power_usage,
        "health": device.health,
        "daily_active_hours": device.daily_active_hours,
        "last_seen": device.last_seen,
        "created_at": getattr(device, "created_at", "") or "",
        "updated_at": getattr(device, "updated_at", "") or "",
    }


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def _score_device(query: str, device: DeviceModel) -> float:
    target = _normalize(query)
    candidates = [
        _normalize(device.name),
        _normalize(f"{getattr(device, 'room', '')} {device.name}"),
        _normalize(f"{getattr(device, 'room', '')} {device.category}"),
        _normalize(device.category),
    ]
    scores = []
    for candidate in candidates:
        if not candidate:
            continue
        if target == candidate:
            scores.append(1.0)
        elif target in candidate or candidate in target:
            # For very short queries (1-2 chars), be more strict
            # Require word boundary match, not substring match
            if len(target) <= 2:
                # Check if target is a complete word in candidate
                if re.search(rf"\b{re.escape(target)}\b", candidate, re.IGNORECASE):
                    scores.append(0.95)
                # Don't add substring match for very short queries
            else:
                scores.append(0.88)
        else:
            scores.append(SequenceMatcher(None, target, candidate).ratio())
    return max(scores or [0])


def find_device(db: Session, device_name: str) -> DeviceModel | None:
    if not device_name or not device_name.strip():
        return None
    devices = list(db.scalars(select(DeviceModel)))
    ranked = sorted(((_score_device(device_name, device), device) for device in devices), reverse=True, key=lambda item: item[0])
    if not ranked or ranked[0][0] < 0.7:
        return None
    return ranked[0][1]


def find_all_devices(db: Session, device_name: str) -> list[DeviceModel]:
    """Find all devices matching the query above threshold."""
    devices = list(db.scalars(select(DeviceModel)))
    ranked = sorted(((_score_device(device_name, device), device) for device in devices), reverse=True, key=lambda item: item[0])
    return [device for score, device in ranked if score >= 0.7]


def toggle_device(db: Session, device_name: str, state: str) -> dict:
    state = state.lower().strip()
    if state not in {"on", "off"}:
        return {"ok": False, "message": "Device state must be on or off.", "changed": False}

    device = find_device(db, device_name)
    if not device:
        return {"ok": False, "message": f"I could not find {device_name}.", "changed": False}

    now = datetime.now().isoformat()
    device.status = state
    device.last_seen = now
    device.updated_at = now
    db.commit()
    db.refresh(device)
    return {
        "ok": True,
        "message": f"{device.name} is now {state}.",
        "changed": True,
        "device": _device_payload(device),
    }


def get_device_status(db: Session, device_name: str) -> dict:
    device = find_device(db, device_name)
    if not device:
        return {"ok": False, "message": f"I could not find {device_name}."}
    load = f" drawing {device.power_usage} watts" if device.status == "on" else f" with a rated load of {device.power_usage} watts"
    return {
        "ok": True,
        "message": f"{device.name} is {device.status}{load}.",
        "device": _device_payload(device),
    }


def get_active_devices(db: Session) -> dict:
    devices = list(db.scalars(select(DeviceModel).where(DeviceModel.status == "on").order_by(DeviceModel.name)))
    names = [device.name for device in devices]
    message = "No devices are currently active." if not names else f"Active devices: {', '.join(names)}."
    return {"ok": True, "message": message, "devices": [_device_payload(device) for device in devices]}


def create_device(db: Session, name: str, category: str, room: str, power_usage: int, daily_active_hours: float = 0) -> dict:
    name = name.strip()
    category = category.strip()
    room = (room or "General").strip() or "General"
    if len(name) < 2:
        return {"ok": False, "message": "Device name must be at least 2 characters.", "changed": False}
    if len(category) < 2:
        return {"ok": False, "message": "Device category must be at least 2 characters.", "changed": False}

    safe_power_usage = max(0, min(int(power_usage), 20000))
    safe_daily_hours = max(0, min(float(daily_active_hours), 24))
    existing = find_device(db, f"{room} {name}")
    if existing and _score_device(f"{room} {name}", existing) > 0.9:
        return {"ok": False, "message": f"{existing.name} already exists.", "changed": False}

    now = datetime.now().isoformat()
    device = DeviceModel(
        id=f"dev-{uuid4().hex[:8]}",
        name=name.title(),
        category=category.title(),
        room=room.title(),
        status="off",
        power_usage=safe_power_usage,
        health="optimal",
        daily_active_hours=safe_daily_hours,
        last_seen=now,
        created_at=now,
        updated_at=now,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {
        "ok": True,
        "message": f"{device.name} has been created in {device.room} at {device.power_usage} watts for {device.daily_active_hours:g} hours daily.",
        "changed": True,
        "device": _device_payload(device),
    }


def delete_device(db: Session, device_name: str) -> dict:
    devices = find_all_devices(db, device_name)
    
    if not devices:
        return {"ok": False, "message": f"I could not find {device_name}.", "changed": False}
    
    if len(devices) > 1:
        device_names = ", ".join([f"{d.room} {d.name}" for d in devices])
        return {
            "ok": False,
            "message": f"I found multiple matches: {device_names}. Which one would you like to delete?",
            "changed": False,
            "vague": True
        }
    
    device = devices[0]
    payload = _device_payload(device)
    db.delete(device)
    db.commit()
    return {
        "ok": True,
        "message": f"{payload['name']} has been removed from VoltStream.",
        "changed": True,
        "device": payload,
    }
