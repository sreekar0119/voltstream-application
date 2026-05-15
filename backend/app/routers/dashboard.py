from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import LiveDashboard
from app.services.dashboard_service import get_live_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live", response_model=LiveDashboard)
def live(db: Session = Depends(get_db)) -> LiveDashboard:
    return LiveDashboard(**get_live_dashboard(db))
