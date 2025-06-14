from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from app.schemas.pyobjectid import PyObjectId # Import PyObjectId

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    name: str
    roles: List[str] = [] # Default to empty list if not provided

class UserCreate(UserBase):
    """Schema for creating a new user (e.g., from an admin panel)."""
    password: str # Assuming a password field for creation
    granted: bool = True # Default to granted on creation, can be changed by admin

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "name": "John Doe",
                "roles": ["user"],
                "password": "securepassword123",
                "granted": True
            }
        }


class User(UserBase):
    """Schema for a user as returned by the API (without sensitive fields like password)."""
    granted: bool

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "name": "John Doe",
                "roles": ["user"],
                "granted": True
            }
        }

class UserInDB(User):
    """Schema for a user as stored in the database (including _id and sensitive fields)."""
    id: PyObjectId = Field(alias="_id") # MongoDB's _id field
    hashed_password: str
    backup_codes: List[str] = []
    min_token_issue_time: int = 0 # Unix timestamp

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}
        arbitrary_types_allowed = True