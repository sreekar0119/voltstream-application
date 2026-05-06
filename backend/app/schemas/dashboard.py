from pydantic import BaseModel


class DashboardMetric(BaseModel):
    label: str
    value: float | int | str
    unit: str
    change: float
    tone: str


class LiveDashboard(BaseModel):
    current_grid_draw: float
    solar_generation: float
    active_devices: int
    total_devices: int
    net_energy_usage: float
    projected_energy_cost: float
    budget_status: str
    budget_used_percent: float
    battery_storage_percent: float
    carbon_offset_today: float
    home_efficiency_score: int
    metrics: list[DashboardMetric]
