from app.schemas.billing import BillingRecord
from app.models import BillingRecordModel
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_billing_records(db: Session) -> list[BillingRecord]:
    records = db.scalars(select(BillingRecordModel).order_by(BillingRecordModel.month))
    return [BillingRecord(**record.__dict__) for record in records]


def get_billing_summary(db: Session) -> dict:
    records = get_billing_records(db)
    latest = records[-1]
    previous = records[-2]
    annual_spend = round(sum(record.bill_amount for record in records), 2)
    annual_savings = round(sum(record.solar_savings for record in records), 2)
    average_bill = round(annual_spend / len(records), 2)
    trend = round(((latest.bill_amount - previous.bill_amount) / previous.bill_amount) * 100, 1)

    return {
        "records": records,
        "latest": latest,
        "annual_spend": annual_spend,
        "annual_savings": annual_savings,
        "average_bill": average_bill,
        "bill_trend_percent": trend,
        "budget_used_percent": round((latest.bill_amount / latest.budget) * 100, 1),
        "budget_exceeded": latest.bill_amount > latest.budget,
        "total_carbon_offset": round(sum(record.carbon_offset for record in records), 1),
    }
