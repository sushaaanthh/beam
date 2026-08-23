from fastapi import APIRouter

from app.api.v1.endpoints import analysis, auth, health, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(analysis.router, tags=["analysis"])
