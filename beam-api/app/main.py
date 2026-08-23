from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.base import Base
from app.database.session import engine
from app.exceptions.handlers import create_exception_handlers
from app.middleware.auth import add_auth_middleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("BEAM AI API starting up - ensuring database tables exist")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")
    yield
    logger.info("BEAM AI API shutting down")


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

    # 1. Add Auth and Exception handlers
    add_auth_middleware(application)
    create_exception_handlers(application)

    # 2. Add CORSMiddleware as the outermost layer
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]
    if settings.BACKEND_CORS_ORIGINS:
        for o in settings.BACKEND_CORS_ORIGINS:
            if o not in cors_origins:
                cors_origins.append(o)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
