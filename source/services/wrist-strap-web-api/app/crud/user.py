# File: app/crud/user.py

import logging
from app.db.session import users_collection
from datetime import datetime, timezone
from typing import Optional

# Get a logger instance for this specific file
logger = logging.getLogger(__name__)


def get_user_by_email(email: str):
    """Finds a user in the database by their email."""
    # This function is called on every request, so we avoid logging here to prevent excessive noise.
    # The outcome (user found/not found) is logged in the security layer which has more context.
    return users_collection.find_one({"email": email})


def set_min_token_issue_time_for_user(user_id: object):
    """
    Sets a new minimum issue time (as a Unix timestamp) for all tokens for a user.
    """
    now_utc = datetime.now(timezone.utc)
    new_iat_floor_ts = int(now_utc.timestamp())

    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"minTokenIssueTime": new_iat_floor_ts}}
    )

    logger.info(f"Set new minimum token issue timestamp for user {user_id} to {new_iat_floor_ts}")


def authenticate_backup_code(user_doc: dict, hashed_code: str) -> Optional[int]:
    """Checks if a hashed backup code is valid and unused for a given user."""
    for i, code_data in enumerate(user_doc.get("backupCodes", [])):
        if code_data.get("codeHash") == hashed_code and not code_data.get("used"):
            return i
    return None


def invalidate_backup_code(user_id: object, code_index: int):
    """Marks a specific backup code as used."""
    logger.info(f"Invalidating backup code at index {code_index} for user ID: {user_id}")
    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {
            f"backupCodes.{code_index}.used": True,
            f"backupCodes.{code_index}.usedAt": current_timestamp
        }}
    )
    logger.info(f"Successfully invalidated backup code for user ID: {user_id}")