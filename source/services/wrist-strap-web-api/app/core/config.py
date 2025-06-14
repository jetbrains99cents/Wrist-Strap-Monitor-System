from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # App metadata
    project_name: str = "Wrist Strap Web API"

    # Default CORS origins (ensure these are clean strings, no Markdown links)
    allowed_hosts: List[str] = [
        "https://172.16.9.183:3001",
        "https://172.21.16.1:3001",
        "https://localhost:3001",
        "http://localhost:3001",
        "https://172.16.9.183:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://127.0.0.1:3000",
    ]

    # App mode
    TEST_MODE: bool = False

    # Database settings
    mongo_details: str
    database_name: str
    device_database_name: str
    mongo_user: str
    mongo_password: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # MQTT Settings # ADD THIS SECTION
    MQTT_BROKER_HOST: str
    MQTT_BROKER_PORT: int
    MQTT_TOPIC_PREFIX: str
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()