from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_token_data, get_current_user, get_database_session
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    SendOtpRequest,
    Token,
    UserCreate,
)
from app.services.auth_service import (
    authenticate_user,
    build_token_response,
    create_user,
    generate_otp_for_user,
    issue_refreshed_tokens,
    reset_user_password_with_otp,
    revoke_refresh_token,
    revoke_token,
)

router = APIRouter(prefix="/auth")


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(
    payload: SendOtpRequest,
    db: Session = Depends(get_database_session),
) -> dict[str, str]:
    return generate_otp_for_user(db, payload.identifier)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    payload: PasswordResetRequest,
    db: Session = Depends(get_database_session),
) -> dict[str, str]:
    reset_user_password_with_otp(db, payload.identifier, payload.otp, payload.new_password)
    return {"message": "Password reset successfully. You can now log in with your new password."}




@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_database_session)) -> dict[str, str]:
    create_user(db, user_in)
    return {"message": "User created successfully"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database_session),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    return build_token_response(user)


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_database_session),
) -> Token:
    return issue_refreshed_tokens(db, refresh_request.refresh_token)


@router.post("/logout")
def logout(
    logout_request: LogoutRequest | None = None,
    current_user: User = Depends(get_current_user),
    current_token_data=Depends(get_current_token_data),
) -> dict[str, str]:
    revoke_token(current_token_data.raw_token)
    if logout_request and logout_request.refresh_token:
        revoke_refresh_token(logout_request.refresh_token)
    return {"message": "Logged out successfully"}
