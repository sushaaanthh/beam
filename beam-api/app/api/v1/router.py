from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    analysis,
    auth,
    chat,
    dashboard,
    health,
    journal,
    notifications,
    privacy,
    reports,
    social,
    users,
    voice,
    wellness,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(journal.router, tags=["journal"])
api_router.include_router(voice.router, tags=["voice"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(wellness.router, tags=["wellness"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(social.router, tags=["social"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(privacy.router, tags=["privacy"])
api_router.include_router(admin.router, tags=["admin"])
