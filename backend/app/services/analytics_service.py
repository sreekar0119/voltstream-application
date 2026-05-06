from app.schemas.analytics import AnalyticsRecord
from app.utils.data_loader import read_json


PERIOD_WINDOWS = {
    "daily": 24,
    "weekly": 24 * 7,
    "monthly": 24 * 30,
}


def get_history(period: str | None = None) -> list[AnalyticsRecord]:
    records = read_json("analytics.json")
    if period:
        records = records[-PERIOD_WINDOWS[period]:]
    return [AnalyticsRecord(**record) for record in records]
