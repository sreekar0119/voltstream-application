from pydantic import BaseModel


class AnalyticsRecord(BaseModel):
    id: str
    timestamp: str
    energy_usage: float
    solar_generation: float
    grid_draw: float
    temperature: float
    voltage: float
    cost: float
