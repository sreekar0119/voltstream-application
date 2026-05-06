from fastapi import APIRouter

from app.schemas.dashboard import LiveDashboard
from app.services.dashboard_service import get_live_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live", response_model=LiveDashboard)
def live() -> LiveDashboard:
    return LiveDashboard(**get_live_dashboard())
