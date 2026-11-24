from app.infrastructure.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import DuplicateEmailError, UserRepository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(self, email: str, password: str):
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
        user = self.users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            # Keep the same public error for unknown email and wrong password.
            raise InvalidCredentialsError("Incorrect email or password")
        return create_access_token(user.id)
