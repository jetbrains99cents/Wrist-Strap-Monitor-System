from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    users,
    devices,
    logs,
    settings # NEW: Import settings router
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"]) # NEW: Include settings router
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])