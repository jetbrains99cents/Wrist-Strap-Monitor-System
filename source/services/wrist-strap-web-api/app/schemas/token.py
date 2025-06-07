# Updated to include the optional 'isTest' flag in the request body.

from pydantic import BaseModel, Field
from typing import Optional, List
from .user import User

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class VerifyBackupCodeRequest(BaseModel):
    email: str = Field(..., example="tan.nguyenthanhduy@vn.sharp-world.com")
    backupCodeHash: str = Field(..., description="The SHA-256 hash of the plain-text backup code.")
    # NEW: Optional flag to prevent invalidating the code during testing.
    isTest: Optional[bool] = False

class TokenPayload(BaseModel):
    sub: Optional[str] = None