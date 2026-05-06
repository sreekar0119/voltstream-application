from fastapi import APIRouter

from app.services.billing_service import get_billing_summary

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/summary")
def summary() -> dict:
    return get_billing_summary()
