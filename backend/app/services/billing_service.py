from app.schemas.billing import BillingRecord
from app.utils.data_loader import read_json


def get_billing_records() -> list[BillingRecord]:
    return [BillingRecord(**record) for record in read_json("billing.json")]


def get_billing_summary() -> dict:
    records = get_billing_records()
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
