from app.schemas.analytics import AnalyticsRecord
from app.models import AnalyticsRecordModel
from sqlalchemy import select
from sqlalchemy.orm import Session


PERIOD_WINDOWS = {
    "daily": 24,
    "weekly": 24 * 7,
    "monthly": 24 * 30,
}


def get_history(db: Session, period: str | None = None) -> list[AnalyticsRecord]:
    statement = select(AnalyticsRecordModel).order_by(AnalyticsRecordModel.timestamp)
    records = list(db.scalars(statement))
    if period:
        records = records[-PERIOD_WINDOWS[period]:]
    return [AnalyticsRecord(**record.__dict__) for record in records]
