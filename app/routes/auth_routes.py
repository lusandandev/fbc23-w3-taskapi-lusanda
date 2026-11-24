"""Expose registration and login endpoints and translate authentication-service errors into HTTP responses."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Build the authentication service with a repository bound to the request session."""
    return AuthService(UserRepository(db))


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(payload: UserRegister, service: AuthService = Depends(get_auth_service)):
    """Register a user and return the public user representation."""
    try:
        return service.register(email=str(payload.email), password=payload.password)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, service: AuthService = Depends(get_auth_service)):
    """Authenticate a user and return a bearer access token with its lifetime."""
    try:
        access_token, expires_in = service.login(
            email=str(payload.email), password=payload.password
        )
        return TokenResponse(access_token=access_token, expires_in=expires_in)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
