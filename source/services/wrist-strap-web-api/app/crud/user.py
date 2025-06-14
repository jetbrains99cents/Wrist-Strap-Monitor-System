# File: app/crud/user.py

import logging
from typing import Optional, Dict, Any
from bson import ObjectId
from datetime import datetime, timezone

from app.schemas.user import UserCreate, UserInDB, User

logger = logging.getLogger(__name__)


def get_user_by_email(db: Any, email: str) -> Optional[Dict[str, Any]]:
    user_doc = db.get_collection("users").find_one({"email": email})
    return user_doc


def get_user_by_id(db: Any, user_id: ObjectId) -> Optional[Dict[str, Any]]:
    user_doc = db.get_collection("users").find_one({"_id": user_id})
    return user_doc


def create_user(db: Any, user: UserCreate) -> Dict[str, Any]:
    user_data = user.model_dump()
    result = db.get_collection("users").insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


def authenticate_backup_code(db: Any, user_doc: Dict[str, Any], backup_code_hash: str) -> Optional[int]:
    """
    Authenticates a backup code for a user by checking the hash AND its 'used' status.
    """
    logger.debug(f"Auth: Attempting to authenticate hash: '{backup_code_hash}' (Type: {type(backup_code_hash)})")

    # NEW DEBUG LOG: Print the entire user_doc received by this function
    logger.debug(f"Auth: user_doc received: {user_doc}")
    logger.debug(f"Auth: user_doc type: {type(user_doc)}")

    # CRITICAL FIX (already applied): Changed from "backup_codes" (snake_case) to "backupCodes" (camelCase)
    backup_codes = user_doc.get("backupCodes", [])

    if not backup_codes:
        logger.debug("Auth: No backup codes array found in user document (checked 'backupCodes' key) or it was empty.")
        return None

    for i, code_entry in enumerate(backup_codes):
        db_code_hash = code_entry.get("codeHash")
        db_code_used = code_entry.get("used")

        logger.debug(
            f"Auth: Comparing with DB entry {i}: Hash='{db_code_hash}' (Type: {type(db_code_hash)}), Used={db_code_used} (Type: {type(db_code_used)})")

        if db_code_hash == backup_code_hash and db_code_used is False:
            logger.info(f"Auth: Matched unused backup code at index {i}.")
            return i
        elif db_code_hash == backup_code_hash and db_code_used is True:
            logger.warning(f"Auth: Matched USED backup code at index {i}. Not authenticating.")
        elif db_code_hash != backup_code_hash:
            logger.debug(f"Auth: Hash mismatch for entry {i}. (DB: '{db_code_hash}', Payload: '{backup_code_hash}')")
        else:
            logger.debug(f"Auth: Other condition not met for entry {i}.")

    logger.warning("Auth: No valid, unused backup code found after checking all entries.")
    return None


def invalidate_backup_code(db: Any, user_id: ObjectId, index: int):
    """Invalidates a specific backup code for a user by setting 'used' to true and 'usedAt'."""
    db.get_collection("users").update_one(
        {"_id": user_id},
        {"$set": {
            f"backup_codes.{index}.used": True,
            f"backup_codes.{index}.usedAt": int(datetime.now(timezone.utc).timestamp() * 1000)
            # Store current timestamp in milliseconds
        }}
    )
    logger.info(f"Invalidated backup code for user {user_id} at index {index}")


def set_min_token_issue_time_for_user(db: Any, user_id: ObjectId):
    """Sets the minimum token issue time for a user (invalidating old tokens)."""
    db.get_collection("users").update_one(
        {"_id": user_id},
        {"$set": {"min_token_issue_time": int(datetime.now(timezone.utc).timestamp())}}
    )
    logger.info(f"Updated min_token_issue_time for user {user_id}")
