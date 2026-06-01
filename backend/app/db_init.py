from __future__ import annotations

from sqlalchemy import select
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models import AnalyticsRecordModel, BillingRecordModel, DeviceModel, UsageHistoryModel
from app.utils.data_loader import read_json


def _seed_table(db: Session, model: type, filename: str) -> None:
    existing_ids = set(db.scalars(select(model.id)))
    records = read_json(filename)
    new_records = []
    seen_ids = set(existing_ids)
    for record in records:
        if record["id"] in seen_ids:
            continue
        seen_ids.add(record["id"])
        new_records.append(record)
    if new_records:
        db.add_all(model(**record) for record in new_records)
        db.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_device_columns()

    with Session(engine) as db:
        _seed_table(db, AnalyticsRecordModel, "analytics.json")
        _seed_table(db, BillingRecordModel, "billing.json")
        _seed_table(db, DeviceModel, "devices.json")
        _seed_usage_history(db)


def _ensure_device_columns() -> None:
    inspector = inspect(engine)
    if "devices" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("devices")}
    statements = []
    if "room" not in columns:
        statements.append("ALTER TABLE devices ADD COLUMN room VARCHAR NOT NULL DEFAULT 'General'")
    if "created_at" not in columns:
        statements.append("ALTER TABLE devices ADD COLUMN created_at VARCHAR NOT NULL DEFAULT ''")
    if "updated_at" not in columns:
        statements.append("ALTER TABLE devices ADD COLUMN updated_at VARCHAR NOT NULL DEFAULT ''")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _seed_usage_history(db: Session) -> None:
    if db.scalar(select(UsageHistoryModel.id).limit(1)):
        return

    devices = list(db.scalars(select(DeviceModel).order_by(DeviceModel.name)))
    analytics = list(db.scalars(select(AnalyticsRecordModel).order_by(AnalyticsRecordModel.timestamp.desc()).limit(168)))
    if not devices or not analytics:
        return

    active_devices = [device for device in devices if device.daily_active_hours > 0] or devices
    total_weight = sum(max(device.power_usage * max(device.daily_active_hours, 1), 1) for device in active_devices)
    rows = []

    for index, record in enumerate(reversed(analytics)):
        for device in active_devices:
            weight = max(device.power_usage * max(device.daily_active_hours, 1), 1) / total_weight
            usage = max(0.01, record.energy_usage * weight)
            rows.append(
                UsageHistoryModel(
                    id=f"usage-{index + 1:04d}-{device.id}",
                    device_name=device.name,
                    energy_usage=round(usage, 3),
                    timestamp=record.timestamp,
                    duration=1.0,
                )
            )

    db.add_all(rows)
    db.commit()
