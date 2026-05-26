import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env path relative to this file so it works regardless of cwd
_ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "kinkyworld"
    DB_USER: str = "kinkyworld"
    DB_PASSWORD: str = "kinkyworld"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ADMIN_KEY: str = "change-this-admin-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()

# Print on import so we can confirm what was loaded
import logging
_log = logging.getLogger("kinkyworld.config")
_log.info(f"DB config → {settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
