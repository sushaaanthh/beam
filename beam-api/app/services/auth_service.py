from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Token, TokenData, UserCreate
from app.services.token_blacklist import blacklist_service


def _normalize_username(username: str) -> str:
    return username.strip()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_username(session: Session, username: str) -> User | None:
    normalized_username = _normalize_username(username)
    return session.scalar(select(User).where(func.lower(User.username) == normalized_username.lower()))


def get_user_by_email(session: Session, email: str) -> User | None:
    normalized_email = _normalize_email(email)
    return session.scalar(select(User).where(func.lower(User.email) == normalized_email))


def get_user_by_identifier(session: Session, identifier: str) -> User | None:
    normalized_identifier = identifier.strip().lower()
    return session.scalar(
        select(User).where(
            (func.lower(User.username) == normalized_identifier)
            | (func.lower(User.email) == normalized_identifier)
        )
    )


def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)


def create_user(session: Session, user_in: UserCreate) -> User:
    username = _normalize_username(user_in.username)
    email = _normalize_email(user_in.email)

    existing_username = get_user_by_username(session, username)
    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    existing_email = get_user_by_email(session, email)
    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )

    session.add(user)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from exc

    session.refresh(user)
    return user


def authenticate_user(session: Session, identifier: str, password: str) -> User:
    user = get_user_by_identifier(session, identifier)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def build_token_response(user: User) -> Token:
    return Token(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id),
        token_type="bearer",
    )


def issue_refreshed_tokens(session: Session, refresh_token: str) -> Token:
    payload = _decode_and_validate_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    try:
        token_data = TokenData.from_payload(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if blacklist_service.is_revoked(token_data.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(session, token_data.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    blacklist_service.revoke(token_data.jti)

    return Token(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id),
        token_type="bearer",
    )


def _decode_and_validate_token(token: str, expected_type: str) -> dict[str, object]:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token_type = str(payload.get("type") or "")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    if not isinstance(jti, str) or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if blacklist_service.is_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def decode_access_token(token: str) -> TokenData:
    payload = _decode_and_validate_token(token, ACCESS_TOKEN_TYPE)
    try:
        return TokenData.from_payload(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def revoke_token(token: str) -> None:
    payload = _decode_and_validate_token(token, ACCESS_TOKEN_TYPE)
    try:
        token_data = TokenData.from_payload(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    blacklist_service.revoke(token_data.jti)


def revoke_refresh_token(token: str) -> None:
    payload = _decode_and_validate_token(token, REFRESH_TOKEN_TYPE)
    try:
        token_data = TokenData.from_payload(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    blacklist_service.revoke(token_data.jti)
