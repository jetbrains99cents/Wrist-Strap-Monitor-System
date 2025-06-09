# File: app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App mode
    TEST_MODE: bool = False

    # Database settings
    mongo_details: str
    database_name: str # This is for the global user DB
    device_database_name: str # NEW: For the service-specific DB
    mongo_user: str
    mongo_password: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()