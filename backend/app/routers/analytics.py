from typing import Literal

from fastapi import APIRouter

from app.schemas.analytics import AnalyticsRecord
from app.services.analytics_service import get_history

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/history", response_model=list[AnalyticsRecord])
def history(period: Literal["daily", "weekly", "monthly"] | None = None) -> list[AnalyticsRecord]:
    return get_history(period)
