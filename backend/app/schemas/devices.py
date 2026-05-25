from pydantic import BaseModel, Field


class Device(BaseModel):
    id: str
    name: str
    category: str
    room: str = "General"
    status: str = Field(pattern="^(on|off)$")
    power_usage: int
    health: str
    daily_active_hours: float
    last_seen: str
    created_at: str = ""
    updated_at: str = ""


class DeviceUpdate(BaseModel):
    status: str = Field(pattern="^(on|off)$")


class DeviceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    category: str = Field(min_length=2, max_length=40)
    room: str = Field(default="General", min_length=2, max_length=40)
    status: str = Field(default="off", pattern="^(on|off)$")
    power_usage: int = Field(ge=0, le=20000)
    health: str = Field(default="optimal", pattern="^(optimal|attention|idle|offline)$")
    daily_active_hours: float = Field(default=0, ge=0, le=24)
