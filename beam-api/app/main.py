from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.exceptions.handlers import create_exception_handlers
from app.middleware.auth import add_auth_middleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("B.E.A.M. API starting up")
    yield
    logger.info("B.E.A.M. API shutting down")


def create_application() -> FastAPI:
    configure_logging()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    add_auth_middleware(application)
    create_exception_handlers(application)
    application.include_router(api_router, prefix=settings.API_V1_STR)

    @application.get("/")
    def root() -> dict[str, str]:
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "status": "running",
        }

    return application


app = create_application()
