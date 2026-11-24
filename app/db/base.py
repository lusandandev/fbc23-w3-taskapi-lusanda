"""SQLAlchemy declarative base shared by all mapped models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class from which all SQLAlchemy mapped models inherit."""
    pass
