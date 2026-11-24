"""Define request and response models used by user registration, login, and token issuance."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Validate the email address and minimum password length required for registration."""
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Validate the credentials supplied to the login endpoint."""
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    """Define the user fields safe to expose in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    """Define the access-token response returned after successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
