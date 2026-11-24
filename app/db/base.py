"""SQLAlchemy declarative base shared by all mapped models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
