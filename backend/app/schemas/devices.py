from pydantic import BaseModel, Field


class Device(BaseModel):
    id: str
    name: str
    category: str
    status: str = Field(pattern="^(on|off)$")
    power_usage: int
    health: str
    daily_active_hours: float
    last_seen: str


class DeviceUpdate(BaseModel):
    status: str = Field(pattern="^(on|off)$")
