# File: app/api/v1/api.py

from fastapi import APIRouter
from .endpoints import auth, users, test  # <-- Import the new test router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(test.router, prefix="/test", tags=["Test"]) # <-- Add the new router
