# Updated to log the incoming request data and handle the new request model.

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from app.schemas.token import TokenResponse, VerifyCodeRequest  # <-- Updated import
from app.schemas.user import User
from app.crud import user as user_crud
from app.security import create_access_token
from app.core.config import settings

print("--- Loading auth.py endpoints ---")  # <-- ADD THIS LINE

router = APIRouter()


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code(request: VerifyCodeRequest):  # <-- Updated to use new request model
    """
    Verifies a user's login code (either a backup code or an email OTP).
    """
    # --- NEW: Added detailed logging ---
    print(f"--- New Login Attempt ---")
    print(f"Received email: {request.email}")
    print(f"Received one-time code: {request.code}")
    print(f"Received backup code hash: {request.backupCodeHash}")
    print(f"--------------------------")

    user_doc = user_crud.get_user_by_email(request.email)

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("granted"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    # --- Logic to handle backup code ---
    if request.backupCodeHash:
        valid_code_index = user_crud.authenticate_backup_code(user_doc, request.backupCodeHash)

        if valid_code_index is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or already used backup code",
            )

        if not settings.TEST_MODE:
            user_crud.invalidate_backup_code(user_doc["_id"], valid_code_index)
            print(f"Backup code at index {valid_code_index} for user {request.email} has been invalidated.")
        else:
            print(f"Global Test Mode is ON. Backup code for user {request.email} was validated but not invalidated.")

    # --- Placeholder logic for future email code ---
    elif request.code:
        # NOTE: This part is not yet functional.
        # You will add logic here to check the `request.code` against a temporary code
        # stored in your database when the email service is implemented.
        print("Email code validation is not yet implemented.")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Email code verification is not yet available."
        )
    else:
        # If neither code is provided, the request is invalid.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code or backup code provided."
        )

    # If validation succeeds, create and return the token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
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
