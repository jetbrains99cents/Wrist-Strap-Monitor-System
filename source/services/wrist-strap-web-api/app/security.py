# File: app/security.py

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import jwt.exceptions
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.schemas.token import TokenPayload
from app.crud import user as user_crud
from app.schemas.user import User

# Get a logger instance for this file
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
        token_iat_timestamp: int = payload.get("iat")

        if email is None or token_iat_timestamp is None:
            raise credentials_exception

        token_data = TokenPayload(sub=email)

    except jwt.ExpiredSignatureError:
        # Use payload from the try block if it exists, otherwise use a placeholder
        user_email = payload.get('sub') if 'payload' in locals() else 'unknown'
        logger.warning(f"Expired token received for email: {user_email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except (jwt.exceptions.InvalidTokenError, jwt.exceptions.PyJWTError) as e:
        logger.error(f"Invalid token error: {e}")
        raise credentials_exception

    user = user_crud.get_user_by_email(email=token_data.sub)
    if user is None:
        logger.warning(f"User not found for email in token: {token_data.sub}")
        raise credentials_exception

    min_issue_time_ts = user.get("minTokenIssueTime")

    if min_issue_time_ts and token_iat_timestamp < min_issue_time_ts:
        gmt7 = timezone(timedelta(hours=7))
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
    return user


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