from datetime import datetime, timedelta, timezone
from typing import Optional, List

import jwt
import jwt.exceptions # ADDED: Import jwt.exceptions to access PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.schemas.token import TokenPayload
from app.crud import user as user_crud
from app.schemas.user import User  # Import the User schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency to get the current user from a JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(sub=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.exceptions.InvalidTokenError, jwt.exceptions.PyJWTError): # MODIFIED: Changed jwt.JWTError to jwt.exceptions.PyJWTError
        raise credentials_exception

    user = user_crud.get_user_by_email(email=token_data.sub)
    if user is None:
        raise credentials_exception

    print(f"[Security] Token validated successfully for user: {user.get('email')}")

    return user


# --- NEW: Dependency for Admin-Only Routes ---
def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that checks if the current user has the 'admin' role.
    If not, it raises a 403 Forbidden error.
    """
    user_roles = current_user.get("roles", [])
    if "admin" not in user_roles:
        print(
            f"[Security] Forbidden: User {current_user.get('email')} with roles {user_roles} tried to access an admin route.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    print(f"[Security] Admin access granted for user: {current_user.get('email')}")
    return current_user