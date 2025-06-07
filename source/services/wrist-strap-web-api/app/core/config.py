# File: app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Field names are lowercase to match Pydantic's default behavior
    mongo_details: str = "mongodb://localhost:27017/?authSource=admin"
    database_name: str = "iot_platform_db"
    mongo_user: str
    mongo_password: str

    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()