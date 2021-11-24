import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Settings Configuration """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    PROJECT_NAME: str = "shop-api"
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

    class Config:
        case_sensitive = True


settings = Settings()
