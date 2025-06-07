# File: app/crud/user.py

from app.db.session import users_collection
from datetime import datetime, timezone
from typing import Optional

def get_user_by_email(email: str):
    """Finds a user in the database by their email."""
    return users_collection.find_one({"email": email})

def authenticate_backup_code(user_doc: dict, hashed_code: str) -> Optional[int]:
    """Checks if a hashed backup code is valid and unused for a given user."""
    for i, code_data in enumerate(user_doc.get("backupCodes", [])):
        if code_data.get("codeHash") == hashed_code and not code_data.get("used"):
            return i  # Return the index of the valid code
    return None # Return None if no valid code is found

def invalidate_backup_code(user_id: object, code_index: int):
    """Marks a specific backup code as used."""
    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {
            f"backupCodes.{code_index}.used": True,
            f"backupCodes.{code_index}.usedAt": current_timestamp
        }}
    )