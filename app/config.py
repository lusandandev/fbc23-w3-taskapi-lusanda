"""Load application configuration exclusively from environment variables."""

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    """Hold the validated application settings as an immutable configuration object."""
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int


def _required(name: str) -> str:
    """Read a required environment variable and reject missing or blank values."""
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value.strip()


# Reuse one validated settings object instead of rereading environment variables on every call.
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate environment configuration, then cache the resulting settings object."""
    database_url = _required("DATABASE_URL")
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("DATABASE_URL must use the PostgreSQL psycopg driver")

    jwt_secret = _required("JWT_SECRET")
    if len(jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters long")

    try:
        access_token_expire_minutes = int(_required("ACCESS_TOKEN_EXPIRE_MINUTES"))
    except ValueError as exc:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer") from exc
    if access_token_expire_minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than zero")

    return Settings(
        database_url=database_url,
        jwt_secret=jwt_secret,
        jwt_algorithm=_required("JWT_ALGORITHM"),
        access_token_expire_minutes=access_token_expire_minutes,
    )
