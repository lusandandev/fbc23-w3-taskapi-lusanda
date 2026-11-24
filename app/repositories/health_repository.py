"""Provide a database connectivity check using the active SQLAlchemy session."""

from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthRepository:
    """Encapsulate the database operation used by the health endpoint."""
    def __init__(self, db: Session) -> None:
        """Store the SQLAlchemy session used for the connectivity check."""
        self.db = db

    def database_is_available(self) -> bool:
        """Execute a lightweight query to verify that the database responds."""
        self.db.execute(text("SELECT 1"))
        return True
