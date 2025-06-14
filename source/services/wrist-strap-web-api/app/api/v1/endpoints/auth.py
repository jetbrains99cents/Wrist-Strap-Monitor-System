# File: app/api/v1/endpoints/auth.py

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from typing import Any

from app.schemas.token import TokenResponse, VerifyCodeRequest
from app.schemas.user import User
from app.crud import user as user_crud
from app.security import create_access_token
from app.core.config import settings
from app.db.session import get_db_global_sync # CHANGED: Import get_db_global_sync

print("--- Loading auth.py endpoints ---")
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: Any = Depends(get_db_global_sync) # CHANGED: Inject the global user DB client here
):
    """
    Verifies a user's login code and issues a new token.
    This action invalidates all previously issued tokens for the user.
    """
    logger.info("--- New Login Attempt ---")
    logger.info(f"Received email: {request.email}")
    logger.info(f"Received backup code hash: {'Yes' if request.backupCodeHash else 'No'}")

    user_doc = user_crud.get_user_by_email(db, request.email)

    if not user_doc:
        logger.warning(f"Login failed: User not found for email {request.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("granted"):
        logger.warning(f"Login failed: User account is disabled for {request.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    if request.backupCodeHash:
        valid_code_index = user_crud.authenticate_backup_code(db, user_doc, request.backupCodeHash)
        if valid_code_index is None:
            logger.warning(f"Login failed: Invalid or used backup code for {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or already used backup code",
            )
        if not settings.TEST_MODE:
            user_crud.invalidate_backup_code(db, user_doc["_id"], valid_code_index)
            logger.info(f"Backup code at index {valid_code_index} for user {request.email} has been invalidated.")
        else:
            logger.info(f"TEST_MODE ON: Backup code for user {request.email} was validated but not invalidated.")

    elif request.code:
        logger.error("Email code verification is not yet implemented.")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Email code verification is not yet available."
        )
    else:
        logger.error("Bad request: No verification code or backup code provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code or backup code provided."
        )

    user_crud.set_min_token_issue_time_for_user(db, user_doc["_id"])

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_doc["email"], "roles": user_doc.get("roles", [])},
        expires_delta=access_token_expires
    )

    user_info = User(**user_doc)
    logger.info(f"Login successful, token issued for {request.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_info
    }