from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.billing_service import get_billing_summary

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    return get_billing_summary(db)
