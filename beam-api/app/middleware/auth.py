from __future__ import annotations

from fastapi import FastAPI
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.security import decode_token
from app.schemas.auth import TokenData
from app.services.token_blacklist import blacklist_service

PUBLIC_PATHS = {
    "/",
    "/docs",
    "/redoc",
    f"{settings.API_V1_STR}/openapi.json",
    f"{settings.API_V1_STR}/health",
    f"{settings.API_V1_STR}/auth/register",
    f"{settings.API_V1_STR}/auth/login",
    f"{settings.API_V1_STR}/auth/refresh",
}

class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if request.method == "OPTIONS" or self._is_public_path(path):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization:
            return await call_next(request)

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return JSONResponse(status_code=401, content={"detail": "Invalid authorization header"})

        try:
            payload = decode_token(token)
            token_data = TokenData.from_payload(payload, raw_token=token)
            if token_data.token_type != "access":
                return JSONResponse(status_code=401, content={"detail": "Invalid token type"})
            if blacklist_service.is_revoked(token_data.jti):
                return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})
        except (JWTError, ValueError):
            return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})

        request.state.token_data = token_data
        request.state.jwt_payload = payload
        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        return path in PUBLIC_PATHS


def add_auth_middleware(app: FastAPI) -> None:
    app.add_middleware(JWTAuthenticationMiddleware)
