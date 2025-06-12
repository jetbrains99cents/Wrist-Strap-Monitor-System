from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    users,
    devices,
    logs,
    settings,
    analytics
)

api_router = APIRouter()

# Ensure all routers are included (uncommented)
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"]) 
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])