"""Configuration settings for the FastAPI application."""
import secrets
from os import getcwd
from os.path import join as join_path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Settings class for the FastAPI application."""
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=join_path(
            getcwd(),
            ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str = "EmonTools"
    EMONCMS_URL: str = ""
    API_KEY: str = ""
    APP_API_KEY: str = ""
    EMON_FINA_PATH: str = "/var/lib/phpfina"
    ARCHIVE_FINA_PATH: str = ""


settings = Settings()
