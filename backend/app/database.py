from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings, BASE_DIR


db_url = settings.database_url
connect_args = {}

if not db_url:
    # Default to local sqlite database
    sqlite_path = BASE_DIR / "voltstream.db"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{sqlite_path}"
    connect_args = {"check_same_thread": False}
elif "://" not in db_url:
    # If it's a file name/path (like "voltstream.db"), resolve it and treat as SQLite
    sqlite_path = Path(db_url)
    if not sqlite_path.is_absolute():
        sqlite_path = BASE_DIR / sqlite_path
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{sqlite_path}"
    connect_args = {"check_same_thread": False}
elif db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


