from __future__ import annotations

from sqlalchemy import select
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

    with Session(engine) as db:
        _seed_table(db, AnalyticsRecordModel, "analytics.json")
        _seed_table(db, BillingRecordModel, "billing.json")
        _seed_table(db, DeviceModel, "devices.json")
