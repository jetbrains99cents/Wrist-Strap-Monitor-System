# File: app/security.py

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Any # ADDED Any for db type hinting

# Assuming 'jwt' and 'jwt.exceptions' are correctly installed for PyJWT
import jwt
import jwt.exceptions
from fastapi import Depends, HTTPException, status # ADDED Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.schemas.token import TokenPayload
from app.crud import user as user_crud
from app.schemas.user import User # This User schema is needed for the return type of get_current_user
from app.db.session import get_db_global_sync # ADDED: Import the dependency for the global user DB


logger = logging.getLogger(__name__)
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


# CHANGED: Added 'db' as a dependency here
def get_current_user(
    db: Any = Depends(get_db_global_sync), # INJECTED: The synchronous global DB client
    token: str = Depends(oauth2_scheme)
) -> dict: # Returning dict as per your existing code, could be UserInDB schema
    """Dependency to get the current user from a JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        token_iat_timestamp: int = payload.get("iat")

        if email is None or token_iat_timestamp is None:
            raise credentials_exception

        token_data = TokenPayload(sub=email)

    except jwt.ExpiredSignatureError:
        user_email = payload.get('sub') if 'payload' in locals() else 'unknown' # Check if payload exists
        logger.warning(f"Expired token received for email: {user_email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.exceptions.InvalidTokenError, jwt.exceptions.PyJWTError) as e:
        logger.error(f"Invalid token error: {e}")
        raise credentials_exception

    # CHANGED: Pass the 'db' object to the CRUD function
    user = user_crud.get_user_by_email(db, email=token_data.sub)
    if user is None:
        logger.warning(f"User not found for email in token: {token_data.sub}")
        raise credentials_exception

    min_issue_time_ts = user.get("minTokenIssueTime") # Uses camelCase from DB

    if min_issue_time_ts and token_iat_timestamp < min_issue_time_ts:
        gmt7 = timezone(timedelta(hours=7)) # Ensure timezone is imported (it is)
        token_iat_dt = datetime.fromtimestamp(token_iat_timestamp, gmt7)
        readable_token_iat = token_iat_dt.strftime("%d-%m-%Y %H:%M:%S")
        min_issue_dt = datetime.fromtimestamp(min_issue_time_ts, gmt7)
        readable_min_issue = min_issue_dt.strftime("%d-%m-%Y %H:%M:%S")

        logger.warning(
            f"Rejected token for user {user.get('email')}. "
            f"Token issue time: {readable_token_iat} GMT+7. "
            f"Required issue time: > {readable_min_issue} GMT+7."
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    logger.info(f"Token validated successfully for user: {user.get('email')}")
    return user # Returns dict, as per your original signature

def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that checks if the current user has the 'admin' role.
    """
    user_roles = current_user.get("roles", [])
    if "admin" not in user_roles:
        logger.warning(
            f"Forbidden: User {current_user.get('email')} with roles {user_roles} tried to access an admin route.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    logger.info(f"Admin access granted for user: {current_user.get('email')}")
    return current_user