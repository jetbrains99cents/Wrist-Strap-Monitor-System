# File: app/api/v1/endpoints/users.py

import logging
from fastapi import APIRouter, Depends
from app.schemas.user import User
from app.security import get_current_user

print("--- Loading users.py endpoints ---")  # <-- ADD THIS LINE

# Get a logger instance for this file
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user.
    """
    # The get_current_user dependency has already done all the work.
    # We add a log here to confirm the action.
    user_email = current_user.get("email")
    logger.info(f"User '{user_email}' successfully fetched their profile data.")

    return current_user
