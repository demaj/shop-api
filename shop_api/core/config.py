from functools import lru_cache

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings Configuration
    """

    model_config = SettingsConfigDict(case_sensitive=True)

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: SecretStr

    PROJECT_NAME: str = "shop-api"
    PROJECT_TITLE: str = "Shop API"
    PROJECT_DESCRIPTION: str = "Shop API Introduction"
    PROJECT_VERSION: str = "0.3.0"

    DATABASE_URI: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()
