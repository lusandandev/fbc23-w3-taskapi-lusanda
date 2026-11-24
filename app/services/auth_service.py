"""Implement registration and login use cases independently of HTTP routing."""

from app.infrastructure.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import DuplicateEmailError, UserRepository


class EmailAlreadyRegisteredError(Exception):
    """Signal that registration cannot use an email already assigned to an account."""
    pass


class InvalidCredentialsError(Exception):
    """Signal that a login attempt did not provide valid credentials."""
    pass


class AuthService:
    """Implement account registration and login using user persistence and security helpers."""
    def __init__(self, users: UserRepository) -> None:
        """Store the user repository used by authentication use cases."""
        self.users = users

    def register(self, email: str, password: str):
        """Normalize the email, hash the password, and create the user account."""
        normalized_email = email.lower()
        if self.users.get_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError("Email is already registered")
        try:
            return self.users.create(
                email=normalized_email, hashed_password=hash_password(password)
            )
        except DuplicateEmailError as exc:
            # Covers two registrations racing after the initial lookup.
            raise EmailAlreadyRegisteredError("Email is already registered") from exc

    def login(self, email: str, password: str) -> tuple[str, int]:
        """Verify the supplied credentials and issue an access token on success."""
        user = self.users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            # Keep the same public error for unknown email and wrong password.
            raise InvalidCredentialsError("Incorrect email or password")
        return create_access_token(user.id)
