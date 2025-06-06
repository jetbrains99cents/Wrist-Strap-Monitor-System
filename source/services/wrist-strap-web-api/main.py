# main.py
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pymongo
import jwt
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# --- Configuration using Pydantic-Settings ---
class Settings(BaseSettings):
    MONGO_DETAILS: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "iot_platform_db"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()

# --- Database Connection ---
try:
    client = pymongo.MongoClient(settings.MONGO_DETAILS)
    db = client[settings.DATABASE_NAME]
    users_collection = db.get_collection("users")
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# --- FastAPI App Initialization ---
app = FastAPI(title="Wrist Strap Web API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---
class User(BaseModel):
    email: str
    name: str
    roles: List[str]
    granted: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class VerifyBackupCodeRequest(BaseModel):
    # Using Ellipsis (...) indicates a required field in Pydantic v2+.
    # PyCharm might show a warning, but this is the correct Pydantic syntax.
    email: str = Field(..., example="tan.nguyenthanhduy@vn.sharp-world.com")
    backupCodeHash: str = Field(..., description="The SHA-256 hash of the plain-text backup code.")


# --- Helper Functions (Updated for PyJWT) ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token using PyJWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Wrist Strap Web API"}


@app.post("/api/auth/verify-code", response_model=TokenResponse)
async def verify_backup_code(request: VerifyBackupCodeRequest):
    user_doc = users_collection.find_one({"email": request.email})

    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user_doc.get("granted"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    code_found = False
    code_index = -1
    for i, code_data in enumerate(user_doc.get("backupCodes", [])):
        if code_data.get("codeHash") == request.backupCodeHash and not code_data.get("used"):
            code_found = True
            code_index = i
            break

    if not code_found:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already used backup code",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    users_collection.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                f"backupCodes.{code_index}.used": True,
                f"backupCodes.{code_index}.usedAt": current_timestamp
            }
        }
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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