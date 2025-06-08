# Updated to include an optional 'code' field for future email verification.

from pydantic import BaseModel, Field
from typing import Optional
from .user import User


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class VerifyCodeRequest(BaseModel):
    """
    This model now handles both backup code and standard email code verification.
    """
    email: str = Field(..., example="tan.nguyenthanhduy@vn.sharp-world.com")

    # Optional field for the standard one-time code sent via email
    code: Optional[str] = None

    # Optional field for the hashed backup code
    backupCodeHash: Optional[str] = Field(None, description="The SHA-256 hash of the plain-text backup code.")


class TokenPayload(BaseModel):
    sub: Optional[str] = None