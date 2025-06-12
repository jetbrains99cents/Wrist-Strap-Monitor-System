# File: app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # App metadata
    project_name: str = "Wrist Strap Web API"

    # Default CORS origins now match your specific list
    allowed_hosts: List[str] = [
        "https://172.16.9.183:3001",  # CORRECTED LINE
        "https://172.21.16.1:3001",  # CORRECTED LINE
        "https://localhost:3001",
        "http://localhost:3001",
        "https://172.16.9.183:3000",  # CORRECTED LINE
        "http://localhost:3000",
        "http://127.0.0.1:3000",  # CORRECTED LINE
        "https://127.0.0.1:3000",  # CORRECTED LINE
    ]

    # App mode
    TEST_MODE: bool = False

    # Database settings
    mongo_details: str
    database_name: str # This is for the global user DB
    device_database_name: str # For the service-specific DB
    mongo_user: str
    mongo_password: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()