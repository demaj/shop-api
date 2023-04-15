import os
from functools import lru_cache

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    """
    Application Settings Configuration
    """

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    PROJECT_NAME: str = "shop-api"
    PROJECT_TITLE: str = "Shop API"
    PROJECT_DESCRIPTION: str = "Shop API.."
    PROJECT_VERSION = "0.1.0"

    DATABASE_URI = os.getenv("DATABASE_URI")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")

    class Config:
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    settings: Settings = Settings()
    return settings
