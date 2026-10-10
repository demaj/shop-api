from functools import lru_cache
from typing import Annotated, Any

from __about__ import __version__
from pydantic import AnyUrl, BeforeValidator, EmailStr, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(value: Any) -> list[str] | str:
    if isinstance(value, str) and not value.startswith("["):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (list, str)):
        return value
    raise ValueError(value)


class Settings(BaseSettings):
    """
    Application Settings Configuration
    """

    model_config = SettingsConfigDict(case_sensitive=True)

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"

    PROJECT_NAME: str = "shop-api"
    PROJECT_TITLE: str = "Shop API"
    PROJECT_DESCRIPTION: str = "Shop API Introduction"
    PROJECT_VERSION: str = __version__

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    DATABASE_URI: str
    DATABASE_CONNECT_TIMEOUT: float = Field(default=5, gt=0)
    DATABASE_POOL_TIMEOUT: float = Field(default=5, gt=0)
    DATABASE_COMMAND_TIMEOUT: float = Field(default=30, gt=0)
    SQL_ECHO: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: SecretStr

    @property
    def cors_origins(self) -> list[str]:
        # AnyUrl normalises to a trailing slash, which breaks CORS origin matching.
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [self.BACKEND_CORS_ORIGINS.rstrip("/")]
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_is_long_enough(cls, value: SecretStr) -> SecretStr:
        # PyJWT warns on HMAC keys under 256 bits.
        if len(value.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters (openssl rand -hex 32)")
        return value

    @field_validator("FIRST_SUPERUSER_PASSWORD")
    @classmethod
    def superuser_password_matches_user_rules(cls, value: SecretStr) -> SecretStr:
        # Fail fast at config load (SecretStr repr is masked, so no leak) rather
        # than starting adminless when the bootstrap's UserCreate rejects it.
        if not 8 <= len(value.get_secret_value()) <= 128:
            raise ValueError("FIRST_SUPERUSER_PASSWORD must be between 8 and 128 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
