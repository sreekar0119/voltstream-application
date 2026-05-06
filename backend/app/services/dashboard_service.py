from __future__ import annotations

import math
from datetime import datetime
from statistics import mean

from app.utils.data_loader import read_json


def _average(records: list[dict], key: str, count: int) -> float:
    sample = records[-count:] if len(records) >= count else records
    return round(mean(record[key] for record in sample), 2)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def get_live_dashboard() -> dict:
    analytics = read_json("analytics.json")
    devices = read_json("devices.json")
    billing = read_json("billing.json")

    latest = analytics[-1]
    previous = analytics[-2]
    today = analytics[-24:]
    active_devices = [device for device in devices if device["status"] == "on"]
    latest_bill = billing[-1]
    month_progress = 0.72

    live_tick = datetime.now().timestamp()
    slow_pulse = math.sin(live_tick / 8)
    fast_pulse = math.sin(live_tick / 3.7)

    current_grid_draw = round(_clamp(latest["grid_draw"] + 0.14 + slow_pulse * 0.11, 0, 7.5), 2)
    solar_generation = round(_clamp(latest["solar_generation"] + slow_pulse * 0.32 + fast_pulse * 0.08, 0, 6.4), 2)
    net_energy_usage = round(latest["energy_usage"] - solar_generation + fast_pulse * 0.05, 2)
    projected_energy_cost = round((sum(record["cost"] for record in today) / 24) * 24 * 30 * (1 + slow_pulse * 0.012), 2)
    budget_used_percent = round((projected_energy_cost / latest_bill["budget"]) * 100 * month_progress, 1)
    solar_today = sum(record["solar_generation"] for record in today)
    usage_today = sum(record["energy_usage"] for record in today)
    efficiency_score = int(max(62, min(99, 82 + (solar_today - usage_today * 0.45))))
    battery_storage = round(_clamp(52 + solar_generation * 7.4 - current_grid_draw * 5.2 + fast_pulse * 1.8, 18, 96), 1)

    return {
        "current_grid_draw": current_grid_draw,
        "solar_generation": solar_generation,
        "active_devices": len(active_devices),
        "total_devices": len(devices),
        "net_energy_usage": net_energy_usage,
        "projected_energy_cost": projected_energy_cost,
        "budget_status": "Over pace" if budget_used_percent > 100 else "On track",
        "budget_used_percent": budget_used_percent,
        "battery_storage_percent": battery_storage,
        "carbon_offset_today": round(solar_today * 0.92 + slow_pulse * 0.4, 1),
        "home_efficiency_score": int(_clamp(efficiency_score + slow_pulse * 2, 62, 99)),
        "metrics": [
            {
                "label": "Solar generation",
                "value": solar_generation,
                "unit": "kW",
                "change": round(solar_generation - previous["solar_generation"], 2),
                "tone": "cyan",
            },
            {
                "label": "Grid draw",
                "value": current_grid_draw,
                "unit": "kW",
                "change": round(current_grid_draw - previous["grid_draw"], 2),
                "tone": "blue",
            },
            {
                "label": "Active devices",
                "value": len(active_devices),
                "unit": "online",
                "change": 0,
                "tone": "green",
            },
            {
                "label": "Projected cost",
                "value": projected_energy_cost,
                "unit": "INR",
                "change": round(projected_energy_cost - _average(billing, "bill_amount", 3), 2),
                "tone": "amber",
            },
        ],
    }
