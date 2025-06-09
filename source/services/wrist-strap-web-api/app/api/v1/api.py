# File: app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, devices, logs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])