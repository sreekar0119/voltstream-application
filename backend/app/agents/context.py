from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from sqlalchemy.orm import Session


current_db: ContextVar[Session | None] = ContextVar("voltstream_current_db", default=None)
current_trace: ContextVar[list[dict[str, Any]] | None] = ContextVar("voltstream_current_trace", default=None)


def require_db() -> Session:
    db = current_db.get()
    if db is None:
        raise RuntimeError("Database session is not available for this ADK tool call.")
    return db


def record_trace(entry: dict[str, Any]) -> None:
    trace = current_trace.get()
    if trace is not None:
        trace.append(entry)
