from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UsageHistoryModel


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _window_start(period: Literal["24h", "7d", "30d", "all"], anchor: datetime) -> datetime | None:
    if period == "24h":
        return anchor - timedelta(hours=24)
    if period == "7d":
        return anchor - timedelta(days=7)
    if period == "30d":
        return anchor - timedelta(days=30)
    return None


def get_usage_history(db: Session, period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict:
    rows = list(db.scalars(select(UsageHistoryModel).order_by(UsageHistoryModel.timestamp.desc())))
    anchor = max((_parse_timestamp(row.timestamp) for row in rows), default=None)
    start = _window_start(period, anchor) if anchor else None
    if start:
        rows = [row for row in rows if (moment := _parse_timestamp(row.timestamp)) and moment >= start]

    rows.sort(key=lambda row: row.timestamp)
    total_kwh = round(sum(row.energy_usage for row in rows), 2)
    device_totals: dict[str, float] = defaultdict(float)
    hourly_totals: dict[int, float] = defaultdict(float)

    for row in rows:
        device_totals[row.device_name] += row.energy_usage
        if moment := _parse_timestamp(row.timestamp):
            hourly_totals[moment.hour] += row.energy_usage

    devices = sorted(
        (
            {"device_name": name, "energy_usage": round(total, 2)}
            for name, total in device_totals.items()
        ),
        key=lambda item: item["energy_usage"],
        reverse=True,
    )
    peak_hour = max(hourly_totals.items(), key=lambda item: item[1], default=(None, 0))

    return {
        "ok": True,
        "period": period,
        "record_count": len(rows),
        "total_kwh": total_kwh,
        "top_devices": devices[:8],
        "peak_hour": peak_hour[0],
        "peak_hour_kwh": round(peak_hour[1], 2),
        "history": [
            {
                "device_name": row.device_name,
                "energy_usage": row.energy_usage,
                "timestamp": row.timestamp,
                "duration": row.duration,
            }
            for row in rows[:240]
        ],
        "message": f"Loaded {len(rows)} usage records for {period}, totaling {total_kwh} kWh.",
    }


def calculate_peak_usage(db: Session, period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict:
    usage = get_usage_history(db, period)
    hourly_totals: dict[str, float] = defaultdict(float)
    device_totals: dict[str, float] = defaultdict(float)

    for row in usage["history"]:
        moment = _parse_timestamp(row["timestamp"])
        if not moment:
            continue
        bucket = moment.strftime("%Y-%m-%d %H:00")
        hourly_totals[bucket] += float(row["energy_usage"])
        device_totals[row["device_name"]] += float(row["energy_usage"])

    peak_window = max(hourly_totals.items(), key=lambda item: item[1], default=(None, 0))
    top_device = max(device_totals.items(), key=lambda item: item[1], default=(None, 0))

    return {
        "ok": True,
        "period": period,
        "peak_window": peak_window[0],
        "peak_kwh": round(peak_window[1], 2),
        "top_device": top_device[0],
        "top_device_kwh": round(top_device[1], 2),
        "message": (
            f"Peak usage was {round(peak_window[1], 2)} kWh around {peak_window[0]}; "
            f"{top_device[0] or 'no device'} contributed the most."
        ),
    }


def summarize_usage_patterns(db: Session, period: Literal["24h", "7d", "30d", "all"] = "7d") -> dict:
    usage = get_usage_history(db, period)
    peak = calculate_peak_usage(db, period)
    top_devices = usage["top_devices"][:3]
    device_text = ", ".join(f"{item['device_name']} ({item['energy_usage']} kWh)" for item in top_devices) or "no devices"

    return {
        "ok": True,
        "period": period,
        "total_kwh": usage["total_kwh"],
        "record_count": usage["record_count"],
        "top_devices": top_devices,
        "peak_window": peak["peak_window"],
        "peak_kwh": peak["peak_kwh"],
        "summary": (
            f"{period} usage totaled {usage['total_kwh']} kWh. "
            f"Highest demand clustered around {peak['peak_window']} at {peak['peak_kwh']} kWh. "
            f"Main contributors: {device_text}."
        ),
    }
