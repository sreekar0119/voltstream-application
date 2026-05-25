from __future__ import annotations

from sqlalchemy import select
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models import AnalyticsRecordModel, BillingRecordModel, DeviceModel
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
