# File: app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends
from app.schemas.user import User
from app.security import get_current_user

print("--- Loading users.py endpoints ---")  # <-- ADD THIS LINE

router = APIRouter()


# UPDATED: The path is now just /me
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user.
    """
    # The get_current_user dependency has already done all the work of
    # validating the token and fetching the user from the database.
    # We just need to return it.
    return current_user
