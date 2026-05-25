from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviceModel


def calculate_total_consumption(db: Session) -> dict:
    active = list(db.scalars(select(DeviceModel).where(DeviceModel.status == "on")))
    watts = sum(device.power_usage for device in active)
    return {
        "ok": True,
        "total_watts": watts,
        "active_count": len(active),
        "message": f"Current active load is {watts} watts across {len(active)} active devices.",
    }


def recommend_energy_saving(db: Session) -> dict:
    devices = list(db.scalars(select(DeviceModel).where(DeviceModel.status == "on")))
    devices.sort(key=lambda device: device.power_usage, reverse=True)
    if not devices:
        return {"ok": True, "message": "Everything is already quiet. No active load is drawing power right now.", "devices": []}

    top = devices[:3]
    names = ", ".join(f"{device.name} ({device.power_usage} W)" for device in top)
    return {
        "ok": True,
        "message": f"Biggest savings opportunity: review {names}. Start with the highest-load device during peak pricing.",
        "devices": [{"name": device.name, "power_usage": device.power_usage, "room": getattr(device, "room", "General")} for device in top],
    }
