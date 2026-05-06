from pydantic import BaseModel


class BillingRecord(BaseModel):
    id: str
    month: str
    bill_amount: float
    solar_savings: float
    usage_kwh: float
    grid_charges: float
    service_fees: float
    carbon_offset: float
    budget: float
