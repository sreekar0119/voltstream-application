from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnalyticsRecordModel(Base):
    __tablename__ = "analytics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    timestamp: Mapped[str] = mapped_column(String, index=True)
    energy_usage: Mapped[float] = mapped_column(Float)
    solar_generation: Mapped[float] = mapped_column(Float)
    grid_draw: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    voltage: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float)


class BillingRecordModel(Base):
    __tablename__ = "billing"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    month: Mapped[str] = mapped_column(String, index=True)
    bill_amount: Mapped[float] = mapped_column(Float)
    solar_savings: Mapped[float] = mapped_column(Float)
    usage_kwh: Mapped[float] = mapped_column(Float)
    grid_charges: Mapped[float] = mapped_column(Float)
    service_fees: Mapped[float] = mapped_column(Float)
    carbon_offset: Mapped[float] = mapped_column(Float)
    budget: Mapped[float] = mapped_column(Float)


class DeviceModel(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    room: Mapped[str] = mapped_column(String, nullable=False, default="General", index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="off")
    power_usage: Mapped[int] = mapped_column(Integer, nullable=False)
    health: Mapped[str] = mapped_column(String, nullable=False, default="optimal")
    daily_active_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    last_seen: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, default="")
    updated_at: Mapped[str] = mapped_column(String, nullable=False, default="")
