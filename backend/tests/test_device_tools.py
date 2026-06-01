from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import DeviceModel
from app.tools.device_tools import toggle_device


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def _device(status: str) -> DeviceModel:
    return DeviceModel(
        id="dev-test",
        name="Lighting Grid",
        category="Lighting",
        room="Living Room",
        status=status,
        power_usage=220,
        health="optimal",
        daily_active_hours=6.7,
        last_seen="2026-05-01T10:00:00",
        created_at="2026-05-01T10:00:00",
        updated_at="2026-05-01T10:00:00",
    )


def test_toggle_device_reports_already_on_without_changing_timestamp() -> None:
    db = _session()
    db.add(_device("on"))
    db.commit()

    result = toggle_device(db, "lighting grid", "on")
    saved = db.get(DeviceModel, "dev-test")

    assert result["ok"] is True
    assert result["changed"] is False
    assert result["message"] == "Lighting Grid is already on."
    assert saved is not None
    assert saved.status == "on"
    assert saved.updated_at == "2026-05-01T10:00:00"


def test_toggle_device_changes_status_when_different() -> None:
    db = _session()
    db.add(_device("off"))
    db.commit()

    result = toggle_device(db, "lighting grid", "on")
    saved = db.get(DeviceModel, "dev-test")

    assert result["ok"] is True
    assert result["changed"] is True
    assert result["message"] == "Lighting Grid is now on."
    assert saved is not None
    assert saved.status == "on"
    assert saved.updated_at != "2026-05-01T10:00:00"
