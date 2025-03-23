"""Configuration settings for the FastAPI application."""
import secrets
from pathlib import Path
from os.path import join as join_path
from urllib.parse import quote_plus
import warnings
from typing import Annotated, Any, Literal
from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    MySQLDsn,
    computed_field,
    model_validator,
)
from typing_extensions import Self
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
# pylint: disable=invalid-name
# ✅ Define the base directory as the root of the `emon_tools/` package
# Moves up to `emon_tools/`
BASE_DIR = Path(__file__).resolve().resolve().parents[3]

# ✅ Ensure `.env` is correctly detected in `emon_tools/`
env_file_path = join_path(BASE_DIR, ".env")


def parse_cors(v: Any) -> list[str] | str:
    """Parse cors string"""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Settings class for the FastAPI application."""
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./fastapi/)
        env_file=env_file_path,
        env_ignore_empty=True,
        extra="ignore",
    )
    print("Env file path: %s", model_config)
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOKEN_ALGORITHM: str = "HS256"
    # 30 minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_COOKIE_EXPIRE_SECONDS: int = 60 * 30

    DATA_BASE_PATH: str
    STATIC_BASE_PATH: str

    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all cors origin"""
        return [
            str(origin).rstrip("/")
            for origin in self.BACKEND_CORS_ORIGINS
        ] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "EmonTools"
    SENTRY_DSN: HttpUrl | None = None
    SELECTED_DB: Literal["Mysql", "Postgres"] = "Mysql"

    MYSQL_SERVER: str
    MYSQL_PORT: int = 3306
    MYSQL_DB: str
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""

    # type: ignore[prop-decorator, C0103]
    @computed_field
    @property
    # Union[PostgresDsn, MySQLDsn]:
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        """Set SqlAlchemy db url"""
        encoded_password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql://{self.MYSQL_USER}:{encoded_password}@"
            f"{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """Check if emails are enabled"""
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("MYSQL_PASSWORD", self.MYSQL_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    EMONCMS_URL: str = ""
    API_KEY: str = ""
    APP_API_KEY: str = ""
    EMON_FINA_PATH: str = "/var/lib/phpfina"
    ARCHIVE_FINA_PATH: str = ""


settings = Settings()
