"""Persist users and retrieve them by their normalized email address."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class DuplicateEmailError(Exception):
    """Signal that the database rejected a user because the email is already registered."""
    pass


class UserRepository:
    """Implement user lookup and persistence using SQLAlchemy."""
    def __init__(self, db: Session) -> None:
        """Store the SQLAlchemy session used for user operations."""
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Find a user by email after normalizing the address to lowercase."""
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def create(self, email: str, hashed_password: str) -> User:
        """Insert a user and translate a unique-email constraint violation into a domain error."""
        user = User(email=email.lower(), hashed_password=hashed_password)
        self.db.add(user)
        try:
            self.db.commit()
        # The unique database constraint also catches two simultaneous registrations of the same email.
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateEmailError("Email is already registered") from exc
        self.db.refresh(user)
        return user
