from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


DEFAULT_SQLITE_URL = "sqlite:///data/expense_tracker.db"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def _ensure_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return

    raw_path = database_url.removeprefix("sqlite:///")
    if raw_path in {"", ":memory:"}:
        return

    Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


def create_db_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    _ensure_sqlite_directory(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from src.db.schema import Base

    Base.metadata.create_all(bind=engine)


def reset_sqlite_db() -> None:
    database_url = get_database_url()
    if not database_url.startswith("sqlite:///"):
        raise ValueError("reset_sqlite_db() is only supported for SQLite databases.")

    raw_path = database_url.removeprefix("sqlite:///")
    if raw_path == ":memory:":
        return

    db_path = Path(raw_path)
    if db_path.exists():
        db_path.unlink()

    init_db()
