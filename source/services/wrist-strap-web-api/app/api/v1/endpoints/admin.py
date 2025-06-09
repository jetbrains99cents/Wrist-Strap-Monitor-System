# File: app/api/v1/endpoints/admin.py

from fastapi import APIRouter, Depends
from app.security import get_current_admin_user
from app.schemas.user import User

print("--- Loading admin.py endpoints ---")  # <-- ADD THIS LINE

router = APIRouter()

@router.get("/dashboard-summary", response_model=dict)
async def get_admin_dashboard(current_user: User = Depends(get_current_admin_user)):
    """
    An example admin-only endpoint.
    It uses the get_current_admin_user dependency to ensure only admins can access it.
    """
    return {"message": f"Welcome Admin {current_user['name']}! Here is your secret dashboard summary."}
