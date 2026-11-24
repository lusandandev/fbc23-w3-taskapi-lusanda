"""Password hashing and signed access-token helpers."""

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from jwt import InvalidTokenError

from app.config import get_settings

_password_hash = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2 before it is stored."""
    return _password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a supplied password and return false for malformed or invalid hashes."""
    try:
        return _password_hash.verify(hashed_password, plain_password)
    except (VerificationError, InvalidHashError, ValueError):
        return False


def create_access_token(user_id: int) -> tuple[str, int]:
    """Sign a JWT containing the user's ID and configured expiration time."""
    settings = get_settings()
    expires_in = settings.access_token_expire_minutes * 60
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    token = jwt.encode(
        # The subject identifies the user; the expiration claim lets JWT validation reject expired tokens.
        {"sub": str(user_id), "exp": expires_at},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_in


def get_user_id_from_token(token: str) -> int | None:
    """Decode a JWT and return its user ID, or None when the token is invalid."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (InvalidTokenError, TypeError, ValueError):
        return None
