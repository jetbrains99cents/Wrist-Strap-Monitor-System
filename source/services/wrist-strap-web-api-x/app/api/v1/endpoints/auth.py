# File: app/api/v1/endpoints/auth.py

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from app.schemas.token import TokenResponse, VerifyBackupCodeRequest
from app.schemas.user import User
from app.crud import user as user_crud
from app.security import create_access_token
from app.core.config import settings

router = APIRouter()


@router.post("/verify-code", response_model=TokenResponse)
async def verify_backup_code(request: VerifyBackupCodeRequest):
    """Verifies a user's email and hashed backup code."""
    user_doc = user_crud.get_user_by_email(request.email)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("granted"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    valid_code_index = user_crud.authenticate_backup_code(user_doc, request.backupCodeHash)

    if valid_code_index is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already used backup code",
        )

    user_crud.invalidate_backup_code(user_doc["_id"], valid_code_index)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_doc["email"], "roles": user_doc.get("roles", [])},
        expires_delta=access_token_expires
    )

    user_info = User(**user_doc)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_info
    }