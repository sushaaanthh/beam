from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: UUID | None = None
    token_type: str | None = None
    jti: str | None = None
    raw_token: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, object], raw_token: str | None = None) -> "TokenData":
        sub = payload.get("sub")
        user_id = UUID(str(sub)) if isinstance(sub, str) and sub else None
        token_type = payload.get("type")
        jti = payload.get("jti")
        return cls(
            user_id=user_id,
            token_type=str(token_type) if isinstance(token_type, str) else None,
            jti=str(jti) if isinstance(jti, str) else None,
            raw_token=raw_token,
        )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
