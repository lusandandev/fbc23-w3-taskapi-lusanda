"""Lazily-created PostgreSQL engine and request-scoped SQLAlchemy sessions."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


# Reuse the engine and session factory across requests rather than creating a new engine each time.
@lru_cache(maxsize=1)
def _get_session_factory() -> sessionmaker[Session]:
    """Create and cache the engine-backed SQLAlchemy session factory."""
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def SessionLocal() -> Session:
    """Return a new session; the PostgreSQL driver is loaded on first use."""
    return _get_session_factory()()


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped session and close it after the request completes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
