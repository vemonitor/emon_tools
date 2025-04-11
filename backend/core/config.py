"""
Configuration settings for the FastAPI application.
This module loads environment settings securely and applies best practices.
"""
import secrets
from urllib.parse import quote_plus
from typing import Annotated, List, Literal
from pydantic import (
    EmailStr,
    HttpUrl,
    MySQLDsn,
    SecretStr,
    computed_field,
    constr,
    model_validator,
    field_validator
)
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from backend.models.shared import ValidationConstants
from backend.utils.paths import ENV_PATH
# pylint: disable=invalid-name


def parse_cors(value: str) -> List[str]:
    """
    Convert a comma-separated string into a list of CORS origins,
    ensuring that each origin is valid (using a simplified host pattern).

    Each origin is stripped of extra whitespace and trailing slashes.
    """
    # Note: Here, you may reuse the HTTP_HOST_REGEX from ValidationConstants.
    host_pattern = ValidationConstants.HTTP_HOST_REGEX
    origins = []
    for origin in value.split(","):
        origin = origin.strip().rstrip("/")
        if not origin:
            continue
        if not host_pattern.match(origin):
            raise ValueError(
                f"Invalid host in BACKEND_CORS_ORIGINS: '{origin}'"
            )
        origins.append(origin)
    if not origins:
        raise ValueError(
            "BACKEND_CORS_ORIGINS must contain at least one valid origin"
        )
    return origins


REQUIRE_UPDATE_FIELDS = [
    "SECRET_KEY", "FIRST_SUPERUSER", "FIRST_SUPERUSER_PASSWORD",
    "MYSQL_PASSWORD"
]


class Settings(BaseSettings):
    """
    Settings for the FastAPI application.
    Loads configurations from environment variables and from an env file.
    """
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        env_ignore_empty=False,
        extra="forbid",
    )
    # Basic settings
    DOMAIN: Annotated[
        str,
        constr(pattern=ValidationConstants.HOST_REGEX.pattern)
    ]
    ENVIRONMENT: Literal["local", "development", "staging", "production"]
    API_V1_STR: Annotated[
        str,
        constr(pattern=ValidationConstants.URL_PATH_STR_REGEX.pattern)
    ]
    PROJECT_NAME: Annotated[
        str,
        constr(pattern=ValidationConstants.KEY_REGEX.pattern)
    ]
    STACK_NAME: Annotated[
        str,
        constr(pattern=ValidationConstants.SLUG_REGEX.pattern)
    ]
    DATA_BASE_PATH: Annotated[
        str,
        constr(pattern=ValidationConstants.UNIX_PATH_REGEX.pattern)
    ]
    STATIC_BASE_PATH: Annotated[
        str,
        constr(pattern=ValidationConstants.UNIX_PATH_REGEX.pattern)
    ]

    # Frontend and CORS configuration
    FRONTEND_HOST: HttpUrl
    # BACKEND_CORS_ORIGINS should be provided
    # as a comma-separated string in the env file.
    BACKEND_CORS_ORIGINS: str
    # ALLOWED_ORIGINS: List[str]

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def validate_cors_origins(cls, v: str) -> List[str]:
        """
        Validate the BACKEND_CORS_ORIGINS environment variable.
        If it's a string, parse it into a list of valid origins.
        """
        if not isinstance(v, str):
            raise ValueError(
                "BACKEND_CORS_ORIGINS must be a comma-separated string."
            )
        return isinstance(parse_cors(v), list)

    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        Combine validated BACKEND_CORS_ORIGINS (as a list)
        with FRONTEND_HOST (host only, without scheme).
        FRONTEND_HOST is stripped of its scheme and trailing slash.
        """
        frontend = self.FRONTEND_HOST
        origins = parse_cors(self.BACKEND_CORS_ORIGINS)
        if frontend not in origins:
            origins.append(frontend)
        return origins

    # Security keys & tokens
    # It is important to change these values for production.
    SECRET_KEY: SecretStr = secrets.token_urlsafe(32)
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: SecretStr
    TOKEN_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_COOKIE_EXPIRE_SECONDS: int = 60 * 30

    @classmethod
    @field_validator("SECRET_KEY", mode="before")
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        """
        Validate the SECRET_KEY environment variable.
        """
        raw = v.get_secret_value()
        if not ValidationConstants.SECRET_KEY_REGEX.match(raw):
            raise ValueError(
                "SECRET_KEY must be at least 32 characters "
                "and include uppercase, lowercase, "
                "digit, and special character."
            )
        return v

    @classmethod
    @field_validator("FIRST_SUPERUSER_PASSWORD", mode="before")
    def validate_superuser_password(cls, v: SecretStr) -> SecretStr:
        """
        Validate the FIRST_SUPERUSER_PASSWORD environment variable.
        """
        raw = v.get_secret_value()
        if not ValidationConstants.PASSWORD_REGEX.match(raw):
            raise ValueError(
                "FIRST_SUPERUSER_PASSWORD must be at least 8 characters "
                "and include at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character."
            )
        return v

    SENTRY_DSN: HttpUrl | None = None
    SELECTED_DB: Literal["Mysql", "Postgres"] = "Mysql"

    MYSQL_HOST: Annotated[
        str,
        constr(pattern=ValidationConstants.HOST_REGEX.pattern)
    ]
    MYSQL_PORT: int
    MYSQL_DB: Annotated[
        str,
        constr(pattern=ValidationConstants.KEY_REGEX.pattern)
    ]
    MYSQL_USER: Annotated[
        str,
        constr(pattern=ValidationConstants.KEY_REGEX.pattern)
    ]
    MYSQL_PASSWORD: SecretStr

    @classmethod
    @field_validator("MYSQL_PORT", mode="before")
    def validate_mysql_port(cls, v: int) -> int:
        """
        Validate the MYSQL_PORT environment variable.
        Ensure it is between 1 and 65535.
        """
        if v < 1 or v > 65535:
            raise ValueError("MYSQL_PORT must be between 1 and 65535")
        return v

    @staticmethod
    def _validate_password(field_name: str, secret: SecretStr) -> SecretStr:
        """
        Shared validator for password fields.
        """
        raw = secret.get_secret_value()
        if not ValidationConstants.PASSWORD_REGEX.match(raw):
            raise ValueError(
                f"{field_name} must be at least 8 characters "
                "and include at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character."
            )
        return secret

    @classmethod
    @field_validator("MYSQL_PASSWORD", mode="before")
    def validate_mysql_password(cls, v: SecretStr) -> SecretStr:
        """
        Validate the MYSQL_PASSWORD environment variable.
        Ensure it meets the password policy.
        """
        return cls._validate_password("MYSQL_PASSWORD", v)

    @computed_field
    @property
    # Union[PostgresDsn, MySQLDsn]:
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        """Set SqlAlchemy db url"""
        validated_password = self._validate_password("MYSQL_PASSWORD", self.MYSQL_PASSWORD)
        encoded_password = quote_plus(validated_password.get_secret_value())
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """Check if emails are enabled"""
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"

    @classmethod
    @model_validator(mode="after")
    def enforce_secure_and_required_values(cls, values: dict) -> dict:
        """
        Ensure all required string fields are non-empty after stripping.
        """
        insecure_default = "changethis"
        # List of fields that must be non-empty.
        required_fields = [
            "DOMAIN", "API_V1_STR", "PROJECT_NAME", "STACK_NAME",
            "DATA_BASE_PATH", "STATIC_BASE_PATH", "FRONTEND_HOST",
            "MYSQL_HOST", "MYSQL_DB", "MYSQL_USER",
            "SECRET_KEY", "FIRST_SUPERUSER", "FIRST_SUPERUSER_PASSWORD",
            "MYSQL_PASSWORD"
        ]
        for field_item in required_fields:
            if not values.get(field_item)\
                    or (isinstance(values.get(field_item), str)
                        and not values[field_item].strip()):
                raise ValueError(
                    f"The environment variable '{field_item}' "
                    "must be provided and not be empty."
                )
        # Enforce that secret values are changed.
        for field_item in REQUIRE_UPDATE_FIELDS:
            val = values[field_item]
            if hasattr(val, "get_secret_value"):
                raw_val = val.get_secret_value()
            else:
                raw_val = val
            if raw_val.strip().lower() == insecure_default:
                raise ValueError(
                    "Insecure value for '{field_item}' "
                    f"(found '{insecure_default}'). "
                    f"Please set a strong, unique value for {field_item}."
                )
        return values


try:
    settings = Settings()
except Exception as e:
    # Raise with a clear error message if validation fails.
    raise RuntimeError(
        f"Configuration validation error:\n {str(e)}") from e

if __name__ == "__main__":
    # For debugging, print out public settings without exposing secrets.
    public_settings = settings.model_dump()
    for field in REQUIRE_UPDATE_FIELDS:
        public_settings.pop(field, None)
    print(public_settings)
