# app/infrastructure/db/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    # === Database ===
    DB_HOST: str = "database"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASS: str = "password"
    DB_NAME: str = "ml_db"

    # === App ===
    APP_NAME: str = "ML_API"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # === Security ===
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # === DB Init flags ===
    INIT_DB_ON_START: bool = True
    INIT_DB_DROP_ALL: bool = True
    DB_ECHO: bool = False

    # === Async DB URL ===
    DATABASE_URL_asyncpg: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def model_post_init(self, __context) -> None:
        if not self.DATABASE_URL_asyncpg:
            self.DATABASE_URL_asyncpg = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
