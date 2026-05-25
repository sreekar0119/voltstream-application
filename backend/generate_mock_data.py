from __future__ import annotations
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "mock_data"

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def generate_analytics() -> list[dict]:
    random.seed(42)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(hours=215)
    records = []

    for index in range(216):
        moment = start + timedelta(hours=index)
        hour = moment.hour
        day_factor = 1 + 0.08 * math.sin(index / 24)

        morning_peak = 1.15 * math.exp(-((hour - 7) ** 2) / 14)
        evening_peak = 1.85 * math.exp(-((hour - 19) ** 2) / 11)
        base_load = 0.55 + morning_peak + evening_peak + random.uniform(-0.08, 0.16)
        usage = clamp(base_load * day_factor, 0.35, 4.8)

        sunlight = math.sin((hour - 6) / 12 * math.pi) if 6 <= hour <= 18 else 0
        cloud_cover = random.uniform(0.78, 1.05)
        solar = clamp(5.8 * max(0, sunlight) * cloud_cover, 0, 6.2)

        grid_draw = max(0, usage - solar * 0.72 + random.uniform(-0.08, 0.12))
        temperature = clamp(69 + 12 * math.sin((hour - 8) / 24 * 2 * math.pi) + random.uniform(-2, 2), 54, 92)
        voltage = clamp(240 + random.uniform(-3.2, 2.8) - grid_draw * 0.25, 232, 246)
        cost = grid_draw * (10.5 if 16 <= hour <= 21 else 7.25)

        records.append(
            {
                "id": f"an-{index + 1:04d}",
                "timestamp": moment.isoformat(),
                "energy_usage": round(usage, 2),
                "solar_generation": round(solar, 2),
                "grid_draw": round(grid_draw, 2),
                "temperature": round(temperature, 1),
                "voltage": round(voltage, 1),
                "cost": round(cost, 2),
            }
        )

    return records


def generate_devices() -> list[dict]:
    devices = [
        ("HVAC Heat Pump", "Climate", 1320, True, "optimal", 8.5),
        ("EV Wall Connector", "Mobility", 6100, False, "idle", 2.2),
        ("Induction Range", "Kitchen", 1800, False, "optimal", 1.1),
        ("Smart Refrigerator", "Kitchen", 180, True, "optimal", 22.8),
        ("Heat Pump Water Heater", "Utility", 940, True, "optimal", 3.8),
        ("Laundry Center", "Utility", 720, False, "optimal", 1.5),
        ("Pool Circulation Pump", "Outdoor", 860, True, "attention", 5.0),
        ("Home Office Circuit", "Workspace", 310, True, "optimal", 9.4),
        ("Lighting Grid", "Lighting", 220, True, "optimal", 6.7),
        ("Battery Inverter", "Energy", 420, True, "optimal", 24.0),
        ("Dishwasher", "Kitchen", 540, False, "idle", 1.0),
        ("Media Wall", "Entertainment", 260, True, "optimal", 4.2),
        ("Garage Workshop", "Utility", 380, False, "offline", 0.4),
    ]
    return [
        {
            "id": f"dev-{index + 1:02d}",
            "name": name,
            "category": category,
            "status": "on" if status else "off",
            "power_usage": watts,
            "health": health,
            "daily_active_hours": hours,
            "last_seen": (datetime.now() - timedelta(minutes=random.randint(1, 55))).isoformat(),
        }
        for index, (name, category, watts, status, health, hours) in enumerate(devices)
    ]


def generate_billing() -> list[dict]:
    random.seed(7)
    now = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    rows = []

    for offset in range(11, -1, -1):
        month = now - timedelta(days=offset * 30)
        season = 1 + 0.18 * math.sin((month.month - 1) / 12 * 2 * math.pi)
        usage = round(random.uniform(760, 1090) * season, 1)
        solar_savings = round(random.uniform(9800, 20400) * (1.08 if 4 <= month.month <= 9 else 0.86), 2)
        grid_charges = round(usage * random.uniform(7.2, 10.8), 2)
        service_fees = round(random.uniform(420, 760), 2)
        bill_amount = max(0, round(grid_charges + service_fees - solar_savings * 0.42, 2))
        carbon_offset = round(usage * random.uniform(0.42, 0.58), 1)

        rows.append(
            {
                "id": f"bill-{month.strftime('%Y-%m')}",
                "month": month.strftime("%b %Y"),
                "bill_amount": bill_amount,
                "solar_savings": solar_savings,
                "usage_kwh": usage,
                "grid_charges": grid_charges,
                "service_fees": service_fees,
                "carbon_offset": carbon_offset,
                "budget": 12500,
            }
        )

    return rows


def write_json(name: str, payload: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    write_json("analytics.json", generate_analytics())
    write_json("devices.json", generate_devices())
    write_json("billing.json", generate_billing())
    print(f"Generated mock datasets in {DATA_DIR}")