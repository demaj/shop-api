from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "shop-api"
    DATABASE_URL: str = "sqlite:///./shop_db.db"

    class Config:
        case_sensitive = True


settings = Settings()
